import fs from 'fs';
import path from 'path';

class LogCorrectionsApplier {
    constructor(logFilePath) {
        this.logFilePath = logFilePath;
        this.appliedFiles = [];
        this.errors = [];
    }

    // Escapar caracteres especiales para regex
    escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // Aplicar correcciones a un archivo específico
    applyCorrectionsToFile(filePath, corrections) {
        try {
            // Leer contenido original
            const originalContent = fs.readFileSync(filePath, 'utf8');
            let modifiedContent = originalContent;
            
            console.log(`\n📝 Aplicando ${corrections.length} corrección(es) en: ${filePath}`);
            
            // Aplicar correcciones de atrás hacia adelante para no alterar posiciones
            const sortedCorrections = [...corrections].sort((a, b) => b.position - a.position);
            
            for (const correction of sortedCorrections) {
                const searchText = correction.original;
                const replacement = correction.replacement;
                
                console.log(`   ✏️  "${searchText}" → "${replacement}"`);
                
                // Buscar y reemplazar todas las ocurrencias
                const regex = new RegExp(`\\b${this.escapeRegExp(searchText)}\\b`, 'g');
                const matches = modifiedContent.match(regex);
                
                if (matches) {
                    modifiedContent = modifiedContent.replace(regex, replacement);
                    console.log(`      ✅ ${matches.length} ocurrencia(s) reemplazada(s)`);
                } else {
                    console.log(`      ⚠️  No se encontró "${searchText}" en el archivo`);
                }
            }
            
            // Escribir archivo modificado
            fs.writeFileSync(filePath, modifiedContent);
            this.appliedFiles.push(filePath);
            console.log(`   ✅ Archivo guardado exitosamente`);
            
        } catch (error) {
            const errorMsg = `Error procesando ${filePath}: ${error.message}`;
            console.error(`   ❌ ${errorMsg}`);
            this.errors.push(errorMsg);
        }
    }

    // Función principal
    async run() {
        console.log('🚀 Aplicando correcciones desde el log JSON...\n');
        
        try {
            // Verificar que el archivo de log existe
            if (!fs.existsSync(this.logFilePath)) {
                console.error(`❌ Archivo de log no encontrado: ${this.logFilePath}`);
                return;
            }
            
            // Leer y parsear el log
            const logContent = fs.readFileSync(this.logFilePath, 'utf8');
            const logData = JSON.parse(logContent);
            
            console.log(`📊 Información del log:`);
            console.log(`   📅 Fecha: ${new Date(logData.timestamp).toLocaleString()}`);
            console.log(`   📁 Archivos analizados: ${logData.totalFilesAnalyzed}`);
            console.log(`   🔍 Archivos con cambios: ${logData.filesWithChanges}`);
            console.log(`   ✏️  Archivos a modificar: ${logData.filesModified}`);
            
            // Filtrar solo archivos que fueron marcados como aplicados
            const filesToApply = logData.details.filter(detail => detail.applied && detail.corrections.length > 0);
            
            if (filesToApply.length === 0) {
                console.log('\n⚠️  No hay correcciones para aplicar en el log');
                return;
            }
            
            console.log(`\n🎯 Aplicando correcciones en ${filesToApply.length} archivo(s):`);
            console.log('━'.repeat(80));
            
            // Aplicar correcciones archivo por archivo
            for (const fileDetail of filesToApply) {
                this.applyCorrectionsToFile(fileDetail.file, fileDetail.corrections);
            }
            
            // Mostrar resumen final
            console.log('\n' + '='.repeat(80));
            console.log('📋 RESUMEN FINAL');
            console.log('='.repeat(80));
            console.log(`✅ Archivos procesados exitosamente: ${this.appliedFiles.length}`);
            console.log(`❌ Errores encontrados: ${this.errors.length}`);
            
            if (this.errors.length > 0) {
                console.log('\n🚨 Errores:');
                this.errors.forEach(error => console.log(`   • ${error}`));
            }
            
            if (this.appliedFiles.length > 0) {
                console.log('\n✅ Archivos modificados:');
                this.appliedFiles.forEach(file => console.log(`   • ${file}`));
            }
            
            console.log('\n🎉 ¡Proceso completado!');
            
        } catch (error) {
            console.error(`❌ Error leyendo el archivo de log: ${error.message}`);
        }
    }
}

// Verificar argumentos de línea de comandos
const args = process.argv.slice(2);
let logFilePath = 'spell-check-log-2025-08-08.json'; // Por defecto

if (args.length > 0) {
    logFilePath = args[0];
}

// Ejecutar el aplicador
const applier = new LogCorrectionsApplier(logFilePath);
applier.run().catch(console.error);