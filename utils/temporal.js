import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Para obtener __dirname en ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class QAExtractor {
  constructor() {
    this.extractedQA = new Map(); // Usar Map para evitar duplicados por pregunta
    this.seenAnswers = new Set(); // Set para evitar respuestas duplicadas
    this.fileStats = {};
  }

  // Buscar archivos recursivamente
  findProjectFiles(dir, extensions = ['.js', '.ts', '.jsx', '.tsx', '.astro']) {
    const files = [];
    const ignoredDirs = ['node_modules', '.git', 'dist', 'build', '.astro', 'utils'];
    
    const searchDir = (currentDir) => {
      try {
        const items = fs.readdirSync(currentDir);
        
        for (const item of items) {
          const fullPath = path.join(currentDir, item);
          const stat = fs.statSync(fullPath);
          
          if (stat.isDirectory()) {
            if (!ignoredDirs.includes(item) && !item.startsWith('.')) {
              searchDir(fullPath);
            }
          } else if (extensions.some(ext => item.endsWith(ext))) {
            files.push(fullPath);
          }
        }
      } catch (error) {
        console.warn(`⚠️ No se pudo acceder a ${currentDir}: ${error.message}`);
      }
    };
    
    searchDir(dir);
    return files;
  }

  // Extraer Q&A con múltiples patrones
  extractFromContent(content, filePath) {
    const patterns = [
      // Patrón principal con comillas dobles
      /{\s*question:\s*"([^"]+)",\s*answer:\s*"([^"]*(?:\\.[^"]*)*?)",?\s*}/gs,
      // Patrón con comillas simples
      /{\s*question:\s*'([^']+)',\s*answer:\s*'([^']*(?:\\.[^']*)*?)',?\s*}/gs,
      // Patrón con template literals
      /{\s*question:\s*`([^`]+)`,\s*answer:\s*`([^`]*(?:\\.[^`]*)*?)`,?\s*}/gs,
      // Patrón más flexible que permite saltos de línea
      /{\s*question:\s*["'`]([^"'`]+)["'`],\s*answer:\s*["'`]([\s\S]*?)["'`],?\s*}/g
    ];

    const results = [];
    
    for (const pattern of patterns) {
      let match;
      pattern.lastIndex = 0; // Reset regex
      
      while ((match = pattern.exec(content)) !== null) {
        const question = match[1].trim();
        let answer = match[2]
          .replace(/\\"/g, '"')
          .replace(/\\'/g, "'")
          .replace(/\s+/g, ' ')
          .trim();
        
        // Limpiar HTML tags si es necesario para mejor lectura
        const cleanAnswer = answer.replace(/<[^>]*>/g, '');
        
        if (question && answer) {
          results.push({
            question,
            answer,
            answerClean: cleanAnswer, // Versión sin HTML
            file: path.relative(process.cwd(), filePath),
            lineNumber: this.getLineNumber(content, match.index)
          });
        }
      }
    }
    
    return results;
  }

  // Obtener número de línea
  getLineNumber(content, index) {
    return content.substring(0, index).split('\n').length;
  }

  // Procesar un archivo
  processFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const qa = this.extractFromContent(content, filePath);
      
      this.fileStats[filePath] = qa.length;
      
      // Agregar al Map usando la pregunta como clave para evitar duplicados
      qa.forEach(item => {
        const cleanAnswerForComparison = item.answerClean.toLowerCase().trim();
        
        // Solo agregar si no existe la pregunta Y no existe una respuesta similar
        if (!this.extractedQA.has(item.question) && !this.seenAnswers.has(cleanAnswerForComparison)) {
          this.extractedQA.set(item.question, item);
          this.seenAnswers.add(cleanAnswerForComparison);
        }
      });
      
      return qa;
    } catch (error) {
      console.error(`❌ Error procesando ${filePath}: ${error.message}`);
      return [];
    }
  }

  // Extraer de todo el proyecto
  extractFromProject(projectPath = '.') {
    console.log('🚀 Iniciando extracción de Q&A del proyecto Astro...\n');
    
    const files = this.findProjectFiles(projectPath);
    console.log(`📁 Analizando ${files.length} archivos...\n`);
    
    let totalFound = 0;
    
    for (const file of files) {
      const qa = this.processFile(file);
      if (qa.length > 0) {
        console.log(`✅ ${path.relative(projectPath, file)}: ${qa.length} Q&A`);
        totalFound += qa.length;
      }
    }
    
    const uniqueCount = this.extractedQA.size;
    const duplicateCount = totalFound - uniqueCount;
    
    console.log(`\n📊 Resumen:`);
    console.log(`   • Total encontrados: ${totalFound}`);
    console.log(`   • Únicos (sin preguntas ni respuestas duplicadas): ${uniqueCount}`);
    console.log(`   • Duplicados omitidos: ${duplicateCount}`);
    
    return Array.from(this.extractedQA.values());
  }

  // Exportar resultados
  exportResults(qa, outputDir = '.') {
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-');
    
    // JSON estructurado
    const jsonOutput = {
      metadata: {
        totalQuestions: qa.length,
        extractedAt: new Date().toISOString(),
        project: "UNE Astro Project",
        fileStats: Object.fromEntries(
          Object.entries(this.fileStats).filter(([_, count]) => count > 0)
        )
      },
      questions: qa.sort((a, b) => a.question.localeCompare(b.question))
    };
    
    const jsonFile = path.join(outputDir, `preguntas-respuestas-${timestamp}.json`);
    fs.writeFileSync(jsonFile, JSON.stringify(jsonOutput, null, 2), 'utf8');
    
    // Texto legible
    const textOutput = `PREGUNTAS Y RESPUESTAS DEL PROYECTO UNE
========================================
Extraídas el: ${new Date().toLocaleString('es-MX')}
Total de preguntas únicas: ${qa.length}

${qa.map((item, index) => {
      return `${index + 1}. PREGUNTA: ${item.question}   

   RESPUESTA: ${item.answerClean}
${'='.repeat(40)}`;
    }).join('\n')}`;
    
    const textFile = path.join(outputDir, `preguntas-respuestas-${timestamp}.txt`);
    fs.writeFileSync(textFile, textOutput, 'utf8');
    
    // CSV para Excel (compatible con acentos)
    const csvHeader = '\ufeffID,Pregunta,Respuesta,Respuesta_Limpia,Archivo,Línea\n'; // BOM para UTF-8
    const csvContent = qa.map((item, index) => {
      const question = `"${item.question.replace(/"/g, '""')}"`;
      const answer = `"${item.answer.replace(/"/g, '""')}"`;
      const answerClean = `"${item.answerClean.replace(/"/g, '""')}"`;
      return `${index + 1},${question},${answer},${answerClean},"${item.file}",${item.lineNumber}`;
    }).join('\n');
    
    const csvFile = path.join(outputDir, `preguntas-respuestas-${timestamp}.csv`);
    fs.writeFileSync(csvFile, csvHeader + csvContent, 'utf8');
    
    console.log(`\n📄 Archivos generados:`);
    console.log(`   • ${path.basename(jsonFile)} (formato estructurado)`);
    console.log(`   • ${path.basename(textFile)} (formato legible)`);
    console.log(`   • ${path.basename(csvFile)} (para Excel)`);
    
    return { jsonFile, textFile, csvFile };
  }
}

// Función principal
async function main() {
  const projectPath = process.argv[2] || path.join(__dirname, '..');
  const outputDir = process.argv[3] || __dirname;
  
  console.log(`🔍 Proyecto: ${path.resolve(projectPath)}`);
  console.log(`📤 Salida: ${path.resolve(outputDir)}\n`);
  
  const extractor = new QAExtractor();
  const qa = extractor.extractFromProject(projectPath);
  
  if (qa.length > 0) {
    const textFile = extractor.exportResults(qa, outputDir);
    console.log(`\n🎉 ¡Extracción completada exitosamente!`);
    console.log(`\nArchivo guardado en: ${textFile}`);
    
    // Mostrar preview de algunas preguntas
    console.log(`\n👀 Preview de las primeras 3 preguntas encontradas:`);
    qa.slice(0, 3).forEach((item, index) => {
      console.log(`\n${index + 1}. ${item.question}`);
      console.log(`   📍 ${item.file}`);
    });
    
  } else {
    console.log(`\n😕 No se encontraron preguntas y respuestas en el proyecto.`);
    console.log(`\nVerifica que:`);
    console.log(`   • El proyecto tiene archivos .js, .ts, .jsx, .tsx o .astro`);
    console.log(`   • Las preguntas siguen el formato: { question: "...", answer: "..." }`);
  }
}

// Ejecutar
main().catch(console.error);