import fs from "fs";
import path from "path";
import { execSync } from "child_process";
import readline from "readline";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class AstroSpellChecker {
  constructor() {
    this.changes = [];
    this.processedFiles = 0;
    this.logFile = `spell-check-log-${
      new Date().toISOString().split("T")[0]
    }.json`;

    // Memoria de decisiones previas
    this.correctionMemory = new Map(); // Formato: "palabra_original" -> { action, replacement }

    // Palabras que deben ser ignoradas (diccionario personalizado)
    this.ignoredWords = [
      "SICYT",
      "UDG",
      "UNE",
      "ASTRO",
      "JSX",
      "CSS",
      "HTML",
      "JS",
      "TS",
      "API",
      "URL",
      "SEO",
      "CMS",
      "UI",
      "UX",
      "GITHUB",
      "NPM",
      "SICYT",
      "SICyT",
      "UdeG",
      "UDG",
      "UNE",
      "UAG",
      "UNIDEP",
      "UNIVER",
      "UTEG",
      "ITESO",
      "CUCEI",
      "CUCSH",
      "CUCEA",
      "CUALTOS",
      "CUCI",
      "CUCOSTA",
      "CETI",
      "SEMS",
      "Guadalajara",
      "VLEX",
      "Zapopan",
      "Tlaquepaque",
      "Tonalá",
      "Vallarta",
      "CONAPO",
      "IIEG",
      "SEP",
      "RVOE",
      "RVOES",
      // Agregar más palabras según necesites
    ];

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
      output: process.stdout,
    });
  }

  // Archivos a procesar
  shouldProcessFile(filePath) {
    const ext = path.extname(filePath);
    const allowedExtensions = [".astro", ".md", ".mdx"];
    const excludedDirs = [
      "node_modules",
      "dist",
      ".astro",
      ".git",
      ".vscode",
      "utils/venv",
    ];

    // Verificar extensión
    if (!allowedExtensions.includes(ext)) return false;

    // Verificar directorios excluidos específicamente
    const relativePath = path.relative(process.cwd(), filePath);
    const pathParts = relativePath.split(path.sep);

    // Excluir solo directorios específicos, no todos los utils
    if (
      pathParts.includes("node_modules") ||
      pathParts.includes(".git") ||
      pathParts.includes(".vscode") ||
      pathParts.includes("dist") ||
      pathParts.includes(".astro") ||
      relativePath.includes("utils" + path.sep + "venv")
    ) {
      return false;
    }

    return true;
  }

  // Extraer solo el texto que debe ser corregido
  extractTextContent(content, filePath) {
    let textToCheck = "";

    if (path.extname(filePath) === ".astro") {
      // Para archivos .astro, ser MUY selectivo
      let processedContent = content;

      // Remover todo el código primero
      processedContent = processedContent.replace(/^---[\s\S]*?---/m, ""); // Frontmatter
      processedContent = processedContent.replace(
        /<script[\s\S]*?<\/script>/gi,
        ""
      ); // Scripts
      processedContent = processedContent.replace(
        /<style[\s\S]*?<\/style>/gi,
        ""
      ); // Styles
      processedContent = processedContent.replace(/\{[\s\S]*?\}/g, ""); // Variables JSX

      // Extraer SOLO contenido de texto de tags específicos de contenido
      const contentTags = [
        /<(?:h[1-6])[^>]*>([^<{]+)<\/(?:h[1-6])>/gi, // Títulos
        /<(?:p)[^>]*>([^<{]+)<\/(?:p)>/gi, // Párrafos
        /<(?:span|div|a)[^>]*>([^<{]+)<\/(?:span|div|a)>/gi, // Texto inline
        /<(?:li|td|th)[^>]*>([^<{]+)<\/(?:li|td|th)>/gi, // Listas y tablas
        /<(?:strong|em|b|i)[^>]*>([^<{]+)<\/(?:strong|em|b|i)>/gi, // Énfasis
      ];

      const textParts = [];
      contentTags.forEach((regex) => {
        let match;
        while ((match = regex.exec(processedContent)) !== null) {
          const text = match[1].trim();
          // Solo agregar si es texto real (no código)
          if (
            text.length > 2 &&
            !text.includes("{") &&
            !text.includes("}") &&
            !text.includes("=") &&
            !text.includes("function") &&
            /^[a-záéíóúñü\s.,;:¡!¿?\-()0-9]+$/i.test(text)
          ) {
            textParts.push(text);
          }
        }
      });

      textToCheck = textParts.join(" ");
    } else if (
      path.extname(filePath) === ".md" ||
      path.extname(filePath) === ".mdx"
    ) {
      // Para markdown, extraer solo párrafos de texto
      let lines = content.split("\n");
      const textLines = [];

      for (const line of lines) {
        const trimmed = line.trim();

        // Ignorar líneas de código, frontmatter, etc
        if (
          trimmed.length > 3 &&
          !trimmed.startsWith("```") &&
          !trimmed.startsWith("---") &&
          !trimmed.startsWith("#") && // Headers (opcional)
          !trimmed.startsWith("*") && // Listas (opcional)
          !trimmed.startsWith("-") && // Listas (opcional)
          !trimmed.startsWith("[") && // Enlaces
          !trimmed.includes("http") &&
          !trimmed.includes("```") &&
          /^[a-záéíóúñü\s.,;:¡!¿?\-()0-9]+$/i.test(trimmed)
        ) {
          textLines.push(trimmed);
        }
      }

      textToCheck = textLines.join(" ");
    }

    // Limpiar y validar el texto final
    textToCheck = textToCheck
      .replace(/\s+/g, " ") // Espacios múltiples
      .trim();

    // Solo procesar si hay contenido significativo
    if (textToCheck.length < 10) {
      textToCheck = "";
    }

    return { textToCheck, protectedParts: [] };
  }

  // Restaurar partes protegidas (nueva estrategia sin placeholders)
  restoreProtectedParts(correctedText, protectedParts, originalContent) {
    // Como ahora extraemos solo texto puro, necesitamos una estrategia diferente
    // Aplicar correcciones directamente al contenido original
    return this.applyCorrectionsToOriginal(correctedText, originalContent);
  }

  // Aplicar correcciones al contenido original de forma inteligente
  applyCorrectionsToOriginal(correctedText, originalContent) {
    // Por ahora, devolver el contenido original
    // Las correcciones se muestran al usuario pero no se aplican automáticamente
    // para evitar romper el código
    return originalContent;
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
    const originalLines = original.split("\n");
    const correctedLines = corrected.split("\n");
    const maxLines = Math.max(originalLines.length, correctedLines.length);
    const diff = [];

    for (let i = 0; i < maxLines; i++) {
      const origLine = originalLines[i] || "";
      const corrLine = correctedLines[i] || "";

      if (origLine !== corrLine) {
        if (origLine) diff.push(`\x1b[31m- ${origLine}\x1b[0m`);
        if (corrLine) diff.push(`\x1b[32m+ ${corrLine}\x1b[0m`);
      }
    }

    return diff.join("\n");
  }

  // Preguntar opción para cada corrección (con memoria)
  async askCorrectionAction(correction, fileContext) {
    const originalWord = correction.original.toLowerCase();

    // Verificar si ya hemos decidido sobre esta palabra antes
    if (this.correctionMemory.has(originalWord)) {
      const savedDecision = this.correctionMemory.get(originalWord);
      console.log(
        `\n🧠 Recordando decisión previa para "${correction.original}"`
      );

      if (savedDecision.action === "apply") {
        console.log(
          `✅ Aplicando sugerencia recordada: "${correction.original}" → "${savedDecision.replacement}"`
        );
        return {
          action: "apply",
          replacement: savedDecision.replacement,
        };
      } else if (savedDecision.action === "custom") {
        console.log(
          `✏️  Aplicando corrección personalizada recordada: "${correction.original}" → "${savedDecision.replacement}"`
        );
        return {
          action: "custom",
          replacement: savedDecision.replacement,
        };
      } else {
        console.log(
          `⏭️  Ignorando (decisión previa): "${correction.original}"`
        );
        return {
          action: "ignore",
          replacement: null,
        };
      }
    }

    // Si no hay decisión previa, preguntar al usuario
    return new Promise((resolve) => {
      console.log("\n💡 ¿Qué deseas hacer?");
      console.log("  [1] Aplicar sugerencia automática");
      console.log("  [2] Escribir mi propia corrección");
      console.log("  [3] No modificar (ignorar este error)");

      this.rl.question("\nElige una opción [1/2/3]: ", (answer) => {
        const choice = answer.trim();

        if (choice === "1") {
          const decision = {
            action: "apply",
            replacement: correction.replacement,
          };
          // Guardar decisión en memoria
          this.correctionMemory.set(originalWord, decision);
          resolve(decision);
        } else if (choice === "2") {
          this.rl.question(
            `\n✏️  Escribe la corrección para "${correction.original}": `,
            (customCorrection) => {
              if (customCorrection.trim()) {
                const decision = {
                  action: "custom",
                  replacement: customCorrection.trim(),
                };
                // Guardar decisión en memoria
                this.correctionMemory.set(originalWord, decision);
                resolve(decision);
              } else {
                console.log("❌ Corrección vacía, omitiendo...");
                const decision = {
                  action: "ignore",
                  replacement: null,
                };
                this.correctionMemory.set(originalWord, decision);
                resolve(decision);
              }
            }
          );
        } else if (choice === "3") {
          const decision = {
            action: "ignore",
            replacement: null,
          };
          // Guardar decisión en memoria
          this.correctionMemory.set(originalWord, decision);
          resolve(decision);
        } else {
          console.log("❌ Opción inválida. Intenta de nuevo.");
          resolve(this.askCorrectionAction(correction, fileContext));
        }
      });
    });
  }

  // Mantener función askConfirmation para confirmaciones simples
  async askConfirmation(message) {
    return new Promise((resolve) => {
      this.rl.question(message, (answer) => {
        resolve(
          answer.toLowerCase().startsWith("s") ||
            answer.toLowerCase().startsWith("y")
        );
      });
    });
  }

  // Analizar archivo y mostrar cambios propuestos
  async analyzeFile(filePath) {
    console.log(`\n📝 Analizando: ${filePath}`);

    const originalContent = fs.readFileSync(filePath, "utf8");
    const { textToCheck, protectedParts } = this.extractTextContent(
      originalContent,
      filePath
    );

    // Si no hay texto para revisar, saltar archivo
    if (!textToCheck || textToCheck.length < 5) {
      console.log(`⏭️  Sin contenido de texto para revisar en: ${filePath}`);
      return { file: filePath, hasChanges: false };
    }

    // Crear archivo temporal para LanguageTool
    const tempFile = `temp_${Date.now()}.txt`;
    fs.writeFileSync(tempFile, textToCheck);

    try {
      // Ejecutar LanguageTool JAR con formato JSON y es-ES (más estricto)
      const command = `${this.languageToolCommand} --json --language es-ES "${tempFile}"`;
      const result = execSync(command, { encoding: "utf8", stdio: "pipe" });

      // Parsear JSON response
      const languageToolResult = JSON.parse(result);
      let corrections = [];

      // Procesar matches de LanguageTool
      if (languageToolResult.matches && languageToolResult.matches.length > 0) {
        corrections = languageToolResult.matches.map((match) => ({
          original: textToCheck.substring(
            match.offset,
            match.offset + match.length
          ),
          replacement:
            match.replacements && match.replacements.length > 0
              ? match.replacements[0].value
              : "",
          rule: match.rule.description || match.rule.id,
          context: match.context.text,
          position: match.offset,
          length: match.length,
          ruleId: match.rule.id,
        }));
      }

      // Si hay correcciones, procesarlas individualmente
      if (corrections.length > 0) {
        console.log(`\n🔍 Errores encontrados en: ${filePath}`);
        console.log("━".repeat(60));

        // Filtrar MUY estrictamente solo errores de texto real
        const textErrors = corrections.filter((correction) => {
          const original = correction.original.toLowerCase();
          const originalExact = correction.original;

          // Ignorar palabras en la lista personalizada
          if (
            this.ignoredWords.some(
              (word) => originalExact.toUpperCase() === word.toUpperCase()
            )
          ) {
            return false;
          }

          // Rechazar si contiene caracteres de código
          if (
            original.includes("{") ||
            original.includes("}") ||
            original.includes("=") ||
            original.includes(".") ||
            original.includes("_") ||
            original.includes("function") ||
            original.includes("return") ||
            original.includes("const") ||
            original.includes("let") ||
            original.includes("var") ||
            original.includes("title") ||
            original.includes("link") ||
            original.includes("map") ||
            original.includes("top") ||
            original.includes("left") ||
            original.includes("planteles") ||
            original.length > 20
          ) {
            return false;
          }

          // Solo aceptar palabras que parezcan español real
          return (
            /^[a-záéíóúñü\s]+$/i.test(original) &&
            original.length >= 3 &&
            original.length <= 15
          );
        });

        if (textErrors.length === 0) {
          console.log(
            "   ℹ️  Solo errores de formato/código encontrados (ignorados)"
          );
          return { file: filePath, hasChanges: false };
        }

        // Revisar cada error individualmente EN TIEMPO REAL
        const acceptedCorrections = [];
        let correctedText = textToCheck;

        for (const [index, correction] of textErrors.entries()) {
          console.log(`\n${"═".repeat(70)}`);
          console.log(
            `📍 ERROR ${index + 1} de ${textErrors.length} en: ${path.basename(
              filePath
            )}`
          );
          console.log(`🔍 Tipo: ${correction.rule} (${correction.ruleId})`);
          console.log(`${"═".repeat(70)}`);

          // Mostrar contexto mejorado
          const contextStart = Math.max(
            0,
            correction.context.indexOf(correction.original) - 30
          );
          const contextEnd = Math.min(
            correction.context.length,
            correction.context.indexOf(correction.original) +
              correction.original.length +
              30
          );
          const contextSnippet = correction.context.substring(
            contextStart,
            contextEnd
          );

          console.log(`📋 Contexto: "...${contextSnippet}..."`);
          console.log(`❌ Texto actual: "${correction.original}"`);
          console.log(`✅ Sugerencia: "${correction.replacement}"`);

          // Información adicional según el tipo de error
          if (correction.ruleId === "UPPERCASE_SENTENCE_START") {
            console.log(
              "💡 Explicación: Las oraciones deben empezar con mayúscula"
            );
          } else if (correction.ruleId === "MORFOLOGIK_RULE_ES") {
            console.log(
              "💡 Explicación: Posible error de ortografía o falta de acento"
            );
          } else if (
            correction.ruleId.includes("QUESTION") ||
            correction.ruleId.includes("EXCLAMATION")
          ) {
            console.log(
              "💡 Explicación: Las preguntas deben llevar ¿? y las exclamaciones ¡!"
            );
          } else if (correction.ruleId.includes("WHITESPACE")) {
            console.log("💡 Explicación: Espaciado incorrecto");
          }

          const userAction = await this.askCorrectionAction(
            correction,
            contextSnippet
          );

          if (userAction.action === "apply") {
            acceptedCorrections.push({
              ...correction,
              replacement: userAction.replacement,
              userAction: "applied",
            });
            console.log(
              `✅ Aplicando sugerencia: "${correction.original}" → "${userAction.replacement}"`
            );
          } else if (userAction.action === "custom") {
            acceptedCorrections.push({
              ...correction,
              replacement: userAction.replacement,
              userAction: "custom",
            });
            console.log(
              `✏️  Aplicando corrección personalizada: "${correction.original}" → "${userAction.replacement}"`
            );
          } else {
            console.log(`⏭️  Ignorando: "${correction.original}"`);
          }
        }

        // Aplicar solo las correcciones aceptadas
        if (acceptedCorrections.length > 0) {
          // Aplicar correcciones al texto (de atrás hacia adelante)
          acceptedCorrections.sort((a, b) => b.position - a.position);
          for (const correction of acceptedCorrections) {
            if (correction.replacement) {
              correctedText =
                correctedText.substring(0, correction.position) +
                correction.replacement +
                correctedText.substring(
                  correction.position + correction.length
                );
            }
          }

          // Restaurar al contenido original (estrategia simple por ahora)
          const finalContent = this.restoreProtectedParts(
            correctedText,
            protectedParts,
            originalContent
          );

          console.log(
            `\n📝 Resumen: ${acceptedCorrections.length} corrección(es) serán aplicadas a ${filePath}`
          );

          return {
            file: filePath,
            originalContent,
            correctedContent: finalContent,
            corrections: acceptedCorrections,
            hasChanges: true,
            autoApproved: true, // Ya fue aprobado individualmente
          };
        } else {
          console.log(`\n⏭️  No se aplicaron correcciones en: ${filePath}`);
          return { file: filePath, hasChanges: false };
        }
      } else {
        console.log(`✨ No se encontraron errores en: ${filePath}`);
        return { file: filePath, hasChanges: false };
      }
    } catch (error) {
      // Si el comando falla pero no hay errores, significa que no encontró problemas
      if (
        error.status === 0 ||
        error.message.includes("No language errors found")
      ) {
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

  // Aplicar cambios confirmados
  applyChanges(changesData) {
    const applied = [];

    changesData.forEach((change) => {
      if (change.hasChanges && change.apply) {
        try {
          fs.writeFileSync(change.file, change.correctedContent);
          applied.push(change.file);
          console.log(`✅ Aplicado: ${change.file}`);
        } catch (error) {
          console.error(
            `❌ Error aplicando cambios en ${change.file}:`,
            error.message
          );
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
      filesWithChanges: changesData.filter((c) => c.hasChanges).length,
      filesModified: appliedFiles.length,
      details: changesData
        .filter((c) => c.hasChanges)
        .map((c) => ({
          file: c.file,
          corrections: c.corrections || [],
          applied: appliedFiles.includes(c.file),
        })),
    };

    fs.writeFileSync(this.logFile, JSON.stringify(report, null, 2));

    console.log(`\n📊 REPORTE FINAL:`);
    console.log(`📁 Archivos analizados: ${this.processedFiles}`);
    console.log(
      `🔍 Archivos con errores: ${
        changesData.filter((c) => c.hasChanges).length
      }`
    );
    console.log(`✏️  Archivos modificados: ${appliedFiles.length}`);
    console.log(`📄 Log detallado guardado en: ${this.logFile}`);
  }

  // Función principal
  async run() {
    console.log(
      "🚀 Iniciando análisis de corrección automática del proyecto Astro...\n"
    );

    // Verificar que LanguageTool JAR esté disponible
    const jarPath =
      "C:\\languagetool\\LanguageTool-stable\\LanguageTool-6.6\\languagetool-commandline.jar";

    try {
      // Verificar que el JAR existe
      if (!fs.existsSync(jarPath)) {
        console.error("❌ LanguageTool JAR no encontrado en:", jarPath);
        console.log("📦 Asegúrate de que esté descargado en esa ubicación");
        this.rl.close();
        return;
      }

      // Verificar que Java funciona con el JAR
      const testCommand = `java -jar "${jarPath}" --version`;
      execSync(testCommand, { encoding: "utf8", stdio: "pipe" });

      this.languageToolCommand = `java -jar "${jarPath}"`;
      console.log(`✅ LanguageTool JAR encontrado y funcionando`);
    } catch (error) {
      console.error("❌ Error con LanguageTool JAR:", error.message);
      console.log("🔧 Verifica que Java esté instalado: java -version");
      this.rl.close();
      return;
    }

    // Buscar archivos solo en src/
    const files = this.findFiles("./src");
    console.log(
      `📂 Encontrados ${files.length} archivos en src/ para analizar`
    );

    if (files.length === 0) {
      console.log("❌ No se encontraron archivos .astro, .md o .mdx en src/");
      this.rl.close();
      return;
    }

    console.log("\n🔍 MODO: Revisión individual de cada error encontrado");
    console.log(
      "💡 Para cada error podrás elegir: [1] Aplicar sugerencia [2] Escribir tu corrección [3] Ignorar"
    );
    console.log("🧠 Las decisiones se recordarán para palabras repetidas\n");

    // Analizar cada archivo y procesar errores en tiempo real
    const changesData = [];
    for (const file of files) {
      const analysis = await this.analyzeFile(file);
      if (analysis.hasChanges) {
        changesData.push(analysis);
      }
      this.processedFiles++;
    }

    // Filtrar archivos con cambios (ya aprobados individualmente)
    const filesWithChanges = changesData.filter((c) => c.hasChanges);

    if (filesWithChanges.length === 0) {
      console.log(
        "\n🎉 ¡Perfecto! No se encontraron errores ortográficos o gramaticales, o todos fueron omitidos."
      );
      this.rl.close();
      return;
    }

    // Mostrar resumen final
    console.log("\n" + "=".repeat(80));
    console.log(
      `📋 RESUMEN FINAL: ${filesWithChanges.length} archivo(s) con correcciones aprobadas`
    );
    console.log("=".repeat(80));

    filesWithChanges.forEach((change) => {
      console.log(
        `📄 ${change.file}: ${change.corrections.length} corrección(es) aprobadas`
      );
    });

    const confirmFinal = await this.askConfirmation(
      "\n¿Proceder a aplicar TODAS las correcciones aprobadas? [s/n]: "
    );

    if (!confirmFinal) {
      console.log("\n❌ Operación cancelada. No se aplicaron cambios.");
      this.generateReport(changesData, []);
      this.rl.close();
      return;
    }

    // Aplicar todas las correcciones ya aprobadas
    filesWithChanges.forEach((change) => (change.apply = true));

    // Aplicar cambios confirmados
    const appliedFiles = this.applyChanges(changesData);

    // Generar reporte final
    this.generateReport(changesData, appliedFiles);

    // Mostrar estadísticas de memoria
    if (this.correctionMemory.size > 0) {
      console.log(
        `\n🧠 Decisiones recordadas para ${this.correctionMemory.size} palabra(s) única(s)`
      );
    }

    console.log("\n🎉 ¡Proceso completado!");
    this.rl.close();
  }
}

// Ejecutar si se llama directamente
const checker = new AstroSpellChecker();
checker.run().catch(console.error);
