import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import readline from 'readline';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class AstroSpellChecker {
    constructor() {
        this.changes = [];
        this.processedFiles = 0;
        this.logFile = `spell-check-log-${new Date().toISOString().split('T')[0]}.json`;
        
        // Patrones para proteger código y rutas
        this.protectedPatterns = [
            // URLs y rutas
            /href=["']([^"']*)["']/g,
            /src=["']([^"']*)["']/g,
            /import\s+.*?from\s+["']([^"']*)["']/g,
            /\.\//g,
            /\.\.?\//g,
            // Clases CSS y IDs
            /class=["']([^"']*)["']/g,
            /id=["']([^"']*)["']/g,
            // Variables y funciones
            /\{[^}]*\}/g,
            // Comentarios de código
            /<!--[\s\S]*?-->/g,
            /\/\*[\s\S]*?\*\//g,
            /\/\/.*$/gm,
            // Código JavaScript/TypeScript
            /<script[\s\S]*?<\/script>/gi,
            /<style[\s\S]*?<\/style>/gi,
            // Atributos de datos
            /data-[a-zA-Z0-9-]*=["']([^"']*)["']/g,
        ];

        // Setup readline interface
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
    }

    // Archivos a procesar
    shouldProcessFile(filePath) {
        const ext = path.extname(filePath);
        const allowedExtensions = ['.astro', '.md', '.mdx'];
        const excludedDirs = ['node_modules', 'dist', '.astro', '.git', '.vscode', 'utils/venv'];
        
        // Verificar extensión
        if (!allowedExtensions.includes(ext)) return false;
        
        // Verificar directorios excluidos específicamente
        const relativePath = path.relative(process.cwd(), filePath);
        const pathParts = relativePath.split(path.sep);
        
        // Excluir solo directorios específicos, no todos los utils
        if (pathParts.includes('node_modules') || 
            pathParts.includes('.git') || 
            pathParts.includes('.vscode') || 
            pathParts.includes('dist') || 
            pathParts.includes('.astro') ||
            relativePath.includes('utils' + path.sep + 'venv')) {
            return false;
        }
        
        return true;
    }

    // Extraer solo el texto que debe ser corregido
    extractTextContent(content, filePath) {
        let textToCheck = content;
        const protectedParts = [];
        let partIndex = 0;

        // Proteger patrones sensibles
        this.protectedPatterns.forEach(pattern => {
            textToCheck = textToCheck.replace(pattern, (match) => {
                const placeholder = `__PROTECTED_${partIndex++}__`;
                protectedParts.push({ placeholder, original: match });
                return placeholder;
            });
        });

        // Para archivos .astro, extraer solo texto visible
        if (path.extname(filePath) === '.astro') {
            // Proteger frontmatter
            textToCheck = textToCheck.replace(/^---[\s\S]*?---/m, (match) => {
                const placeholder = `__FRONTMATTER_${partIndex++}__`;
                protectedParts.push({ placeholder, original: match });
                return placeholder;
            });

            // Proteger tags HTML pero mantener el contenido de texto
            textToCheck = textToCheck.replace(/<([^>]+)>/g, (match) => {
                const placeholder = `__TAG_${partIndex++}__`;
                protectedParts.push({ placeholder, original: match });
                return placeholder;
            });
        }

        return { textToCheck, protectedParts };
    }

    // Restaurar partes protegidas
    restoreProtectedParts(correctedText, protectedParts) {
        let restoredText = correctedText;
        protectedParts.forEach(({ placeholder, original }) => {
            restoredText = restoredText.replace(placeholder, original);
        });
        return restoredText;
    }

    // Buscar archivos recursivamente
    findFiles(dir, files = []) {
        const entries = fs.readdirSync(dir);
        
        for (const entry of entries) {
            const fullPath = path.join(dir, entry);
            const stat = fs.statSync(fullPath);
            
            if (stat.isDirectory()) {
                this.findFiles(fullPath, files);
            } else if (this.shouldProcessFile(fullPath)) {
                files.push(fullPath);
            }
        }
        
        return files;
    }

    // Generar diff visual de cambios
    generateDiff(original, corrected) {
        const originalLines = original.split('\n');
        const correctedLines = corrected.split('\n');
        const maxLines = Math.max(originalLines.length, correctedLines.length);
        const diff = [];

        for (let i = 0; i < maxLines; i++) {
            const origLine = originalLines[i] || '';
            const corrLine = correctedLines[i] || '';
            
            if (origLine !== corrLine) {
                if (origLine) diff.push(`\x1b[31m- ${origLine}\x1b[0m`);
                if (corrLine) diff.push(`\x1b[32m+ ${corrLine}\x1b[0m`);
            }
        }

        return diff.join('\n');
    }

    // Analizar archivo y mostrar cambios propuestos
    async analyzeFile(filePath) {
        console.log(`\n📝 Analizando: ${filePath}`);
        
        const originalContent = fs.readFileSync(filePath, 'utf8');
        const { textToCheck, protectedParts } = this.extractTextContent(originalContent, filePath);
        
        // Crear archivo temporal para LanguageTool
        const tempFile = `temp_${Date.now()}.txt`;
        fs.writeFileSync(tempFile, textToCheck);
        
        try {
            // Ejecutar LanguageTool JAR con formato JSON y es-ES (más estricto)
            const command = `${this.languageToolCommand} --json --language es-ES "${tempFile}"`;
            const result = execSync(command, { encoding: 'utf8', stdio: 'pipe' });
            
            // Parsear JSON response
            const languageToolResult = JSON.parse(result);
            let corrections = [];
            
            // Procesar matches de LanguageTool
            if (languageToolResult.matches && languageToolResult.matches.length > 0) {
                corrections = languageToolResult.matches.map(match => ({
                    original: textToCheck.substring(match.offset, match.offset + match.length),
                    replacement: match.replacements && match.replacements.length > 0 ? match.replacements[0].value : '',
                    rule: match.rule.description || match.rule.id,
                    context: match.context.text,
                    position: match.offset,
                    length: match.length,
                    ruleId: match.rule.id
                }));
            }
            
            // Si hay correcciones, aplicarlas
            if (corrections.length > 0) {
                let correctedText = textToCheck;
                
                // Aplicar correcciones (de atrás hacia adelante para no alterar índices)
                corrections.sort((a, b) => b.position - a.position);
                
                for (const correction of corrections) {
                    if (correction.replacement) {
                        correctedText = correctedText.substring(0, correction.position) + 
                                      correction.replacement + 
                                      correctedText.substring(correction.position + correction.length);
                    }
                }
                
                // Restaurar partes protegidas
                const finalContent = this.restoreProtectedParts(correctedText, protectedParts);
                
                console.log(`\n🔍 Cambios propuestos para: ${filePath}`);
                console.log('━'.repeat(60));
                
                corrections.forEach((correction, index) => {
                    console.log(`\n${index + 1}. ${correction.rule} (${correction.ruleId})`);
                    console.log(`   Contexto: "${correction.context}"`);
                    console.log(`   \x1b[31m- "${correction.original}"\x1b[0m`);
                    console.log(`   \x1b[32m+ "${correction.replacement}"\x1b[0m`);
                });
                
                return {
                    file: filePath,
                    originalContent,
                    correctedContent: finalContent,
                    corrections,
                    hasChanges: true
                };
            } else {
                console.log(`✨ No se encontraron errores en: ${filePath}`);
                return { file: filePath, hasChanges: false };
            }
            
        } catch (error) {
            // Si el comando falla pero no hay errores, significa que no encontró problemas
            if (error.status === 0 || error.message.includes('No language errors found')) {
                console.log(`✨ No se encontraron errores en: ${filePath}`);
                return { file: filePath, hasChanges: false };
            }
            console.error(`❌ Error analizando ${filePath}:`, error.message);
            return { file: filePath, hasChanges: false, error: error.message };
        } finally {
            // Limpiar archivo temporal
            if (fs.existsSync(tempFile)) {
                fs.unlinkSync(tempFile);
            }
        }
    }

    // Preguntar confirmación al usuario
    async askConfirmation(message) {
        return new Promise((resolve) => {
            this.rl.question(message, (answer) => {
                resolve(answer.toLowerCase().startsWith('s') || answer.toLowerCase().startsWith('y'));
            });
        });
    }

    // Aplicar cambios confirmados
    applyChanges(changesData) {
        const applied = [];
        
        changesData.forEach(change => {
            if (change.hasChanges && change.apply) {
                try {
                    fs.writeFileSync(change.file, change.correctedContent);
                    applied.push(change.file);
                    console.log(`✅ Aplicado: ${change.file}`);
                } catch (error) {
                    console.error(`❌ Error aplicando cambios en ${change.file}:`, error.message);
                }
            }
        });

        return applied;
    }

    // Generar reporte de cambios
    generateReport(changesData, appliedFiles) {
        const report = {
            timestamp: new Date().toISOString(),
            totalFilesAnalyzed: this.processedFiles,
            filesWithChanges: changesData.filter(c => c.hasChanges).length,
            filesModified: appliedFiles.length,
            details: changesData.filter(c => c.hasChanges).map(c => ({
                file: c.file,
                corrections: c.corrections || [],
                applied: appliedFiles.includes(c.file)
            }))
        };
        
        fs.writeFileSync(this.logFile, JSON.stringify(report, null, 2));
        
        console.log(`\n📊 REPORTE FINAL:`);
        console.log(`📁 Archivos analizados: ${this.processedFiles}`);
        console.log(`🔍 Archivos con errores: ${changesData.filter(c => c.hasChanges).length}`);
        console.log(`✏️  Archivos modificados: ${appliedFiles.length}`);
        console.log(`📄 Log detallado guardado en: ${this.logFile}`);
    }

    // Función principal
    async run() {
        console.log('🚀 Iniciando análisis de corrección automática del proyecto Astro...\n');
        
        // Verificar que LanguageTool JAR esté disponible
        const jarPath = "C:\\languagetool\\LanguageTool-stable\\LanguageTool-6.6\\languagetool-commandline.jar";
        
        try {
            // Verificar que el JAR existe
            if (!fs.existsSync(jarPath)) {
                console.error('❌ LanguageTool JAR no encontrado en:', jarPath);
                console.log('📦 Asegúrate de que esté descargado en esa ubicación');
                this.rl.close();
                return;
            }
            
            // Verificar que Java funciona con el JAR
            const testCommand = `java -jar "${jarPath}" --version`;
            execSync(testCommand, { encoding: 'utf8', stdio: 'pipe' });
            
            this.languageToolCommand = `java -jar "${jarPath}"`;
            console.log(`✅ LanguageTool JAR encontrado y funcionando`);
            
        } catch (error) {
            console.error('❌ Error con LanguageTool JAR:', error.message);
            console.log('🔧 Verifica que Java esté instalado: java -version');
            this.rl.close();
            return;
        }
        
        // Buscar archivos solo en src/
        const files = this.findFiles('./src');
        console.log(`📂 Encontrados ${files.length} archivos en src/ para analizar`);
        
        // Debug: mostrar algunos archivos encontrados
        if (files.length > 0) {
            console.log('📋 Archivos a procesar:');
            files.slice(0, 10).forEach(file => console.log(`   • ${file}`));
            if (files.length > 10) {
                console.log(`   ... y ${files.length - 10} archivos más`);
            }
        }
        console.log('');
        
        // Analizar cada archivo
        const changesData = [];
        for (const file of files) {
            const analysis = await this.analyzeFile(file);
            changesData.push(analysis);
            this.processedFiles++;
        }
        
        // Filtrar archivos con cambios
        const filesWithChanges = changesData.filter(c => c.hasChanges);
        
        if (filesWithChanges.length === 0) {
            console.log('\n🎉 ¡Perfecto! No se encontraron errores ortográficos o gramaticales.');
            this.rl.close();
            return;
        }
        
        // Mostrar resumen y pedir confirmación
        console.log('\n' + '='.repeat(80));
        console.log(`📋 RESUMEN: Se encontraron errores en ${filesWithChanges.length} archivo(s)`);
        console.log('='.repeat(80));
        
        filesWithChanges.forEach(change => {
            console.log(`📄 ${change.file}: ${change.corrections.length} corrección(es)`);
        });
        
        console.log('\n💡 Opciones:');
        console.log('  [s] Aplicar TODOS los cambios');
        console.log('  [n] Cancelar (no aplicar ningún cambio)');
        console.log('  [i] Revisar archivo por archivo');
        
        const globalChoice = await new Promise((resolve) => {
            this.rl.question('\n¿Qué deseas hacer? [s/n/i]: ', resolve);
        });
        
        if (globalChoice.toLowerCase() === 'n') {
            console.log('\n❌ Operación cancelada. No se aplicaron cambios.');
            this.generateReport(changesData, []);
            this.rl.close();
            return;
        }
        
        if (globalChoice.toLowerCase() === 's') {
            // Aplicar todos los cambios
            filesWithChanges.forEach(change => change.apply = true);
        } else {
            // Revisar archivo por archivo
            for (const change of filesWithChanges) {
                console.log(`\n${'─'.repeat(60)}`);
                console.log(`📄 ${change.file} (${change.corrections.length} corrección(es))`);
                
                const applyFile = await this.askConfirmation('¿Aplicar cambios en este archivo? [s/n]: ');
                change.apply = applyFile;
                
                if (applyFile) {
                    console.log(`✓ Programado para aplicar: ${change.file}`);
                } else {
                    console.log(`✗ Omitido: ${change.file}`);
                }
            }
        }
        
        // Aplicar cambios confirmados
        const appliedFiles = this.applyChanges(changesData);
        
        // Generar reporte final
        this.generateReport(changesData, appliedFiles);
        
        console.log('\n🎉 ¡Proceso completado!');
        this.rl.close();
    }
}

// Ejecutar si se llama directamente
const checker = new AstroSpellChecker();
checker.run().catch(console.error);