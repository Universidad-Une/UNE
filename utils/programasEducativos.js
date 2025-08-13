// Datos de programas educativos organizados por nivel, área y plantel
// Generado automáticamente desde datos de Excel

export const programasEducativos = {
  Licenciaturas: {
    "Arquitectura y diseño": {
      "Diseño Gráfico": {
        "UNE  EN  LÍNEA": [
          {
            modalidad: "Escolarizada",
            incorporacion: "SICYT",
            hoja_fuente: "GDL",
          },
        ],
      },
      "Ingeniería Industrial": {
        "UNE  EN  LÍNEA": [
          {
            modalidad: "Escolarizada",
            incorporacion: "SICYT",
            hoja_fuente: "GDL",
          },
        ],
      },
    },
    "Ciencias Sociales y Humanidades": {
      Comunicación: {
        "UNE  EN  LÍNEA": [
          {
            modalidad: "Escolarizada",
            incorporacion: "SICYT",
            hoja_fuente: "GDL",
          },
        ],
      },
      Derecho: {
        "UNE  EN  LÍNEA": [
          {
            modalidad: "Escolarizada",
            incorporacion: "SICYT",
            hoja_fuente: "GDL",
          },
        ],
      },
      "Licenciatura en Educación": {
        "UNE  EN  LÍNEA": [
          {
            modalidad: "Escolarizada",
            incorporacion: "SICYT",
            hoja_fuente: "GDL",
          },
        ],
      },
    },
    "Ciencias de la salud": {
      Psicología: {
        "UNE  EN  LÍNEA": [
          {
            modalidad: "Escolarizada",
            incorporacion: "SICYT",
            hoja_fuente: "GDL",
          },
        ],
      },
    },
    "Económico Administrativa": {
      Administración: {
        "UNE  EN  LÍNEA": [
          {
            modalidad: "Escolarizada",
            incorporacion: "SICYT",
            hoja_fuente: "GDL",
          },
        ],
      },
      "Administración de Sistemas de Información": {
        "UNE  EN  LÍNEA": [
          {
            modalidad: "Escolarizada",
            incorporacion: "SICYT",
            hoja_fuente: "GDL",
          },
        ],
      },
      "Comercio y Negocios Globales": {
        "UNE  EN  LÍNEA": [
          {
            modalidad: "En línea",
            incorporacion: "SICYT",
            hoja_fuente: "GDL",
          },
        ],
      },
      Contaduría: {
        "UNE  EN  LÍNEA": [
          {
            modalidad: "Escolarizada",
            incorporacion: "SICYT",
            hoja_fuente: "GDL",
          },
        ],
      },
      Mercadotecnia: {
        "UNE  EN  LÍNEA": [
          {
            modalidad: "Escolarizada",
            incorporacion: "SICYT",
            hoja_fuente: "GDL",
          },
        ],
      },
    },
  },
};

// Funciones de utilidad para consultar los datos

export const areas = [
  "Todas",
  "Económico Administrativa",
  "Ciencias de la salud",
  "Arquitectura y diseño",
  "Gastronomía",
  "Ciencias Sociales y Humanidades",
  "Ciencias exactas e ingenierías",
];

export const niveles = Object.keys(programasEducativos);

/**
 * Obtiene todos los programas de un nivel educativo específico
 * @param {string} nivel - Nivel educativo
 * @returns {Object} Programas del nivel especificado
 */
export function obtenerProgramasPorNivel(nivel) {
  return programasEducativos[nivel] || {};
}

/**
 * Obtiene todos los programas de un área específica
 * @param {string} area - Área de conocimiento
 * @param {string} nivel - Nivel educativo (opcional)
 * @returns {Object} Programas del área especificada
 */
export function obtenerProgramasPorArea(area, nivel = null) {
  const resultado = {};

  if (nivel) {
    return programasEducativos[nivel]?.[area] || {};
  }

  for (const nivelKey in programasEducativos) {
    if (programasEducativos[nivelKey][area]) {
      resultado[nivelKey] = programasEducativos[nivelKey][area];
    }
  }

  return resultado;
}

/**
 * Busca programas por nombre (búsqueda parcial)
 * @param {string} termino - Término de búsqueda
 * @returns {Array} Array de programas que coinciden con el término
 */
export function buscarProgramas(termino) {
  const resultados = [];
  const terminoLower = termino.toLowerCase();

  for (const nivel in programasEducativos) {
    for (const area in programasEducativos[nivel]) {
      for (const programa in programasEducativos[nivel][area]) {
        if (programa.toLowerCase().includes(terminoLower)) {
          resultados.push({
            programa,
            nivel,
            area,
            planteles: Object.keys(programasEducativos[nivel][area][programa]),
          });
        }
      }
    }
  }

  return resultados;
}

/**
 * Obtiene información detallada de un programa específico
 * @param {string} programa - Nombre del programa
 * @param {string} plantel - Nombre del plantel
 * @returns {Object|null} Información del programa o null si no existe
 */
export function obtenerDetallePrograma(programa, plantel) {
  for (const nivel in programasEducativos) {
    for (const area in programasEducativos[nivel]) {
      if (programasEducativos[nivel][area][programa]?.[plantel]) {
        return {
          programa,
          nivel,
          area,
          plantel,
          detalles: programasEducativos[nivel][area][programa][plantel],
        };
      }
    }
  }
  return null;
}

/**
 * Obtiene estadísticas generales de los datos
 * @returns {Object} Estadísticas de los programas
 */
export function obtenerEstadisticas() {
  let totalProgramas = 0;
  const planteles = new Set();
  const estadisticasPorNivel = {};
  const estadisticasPorArea = {};

  for (const nivel in programasEducativos) {
    estadisticasPorNivel[nivel] = 0;

    for (const area in programasEducativos[nivel]) {
      if (!estadisticasPorArea[area]) {
        estadisticasPorArea[area] = 0;
      }

      for (const programa in programasEducativos[nivel][area]) {
        totalProgramas++;
        estadisticasPorNivel[nivel]++;
        estadisticasPorArea[area]++;

        for (const plantel in programasEducativos[nivel][area][programa]) {
          planteles.add(plantel);
        }
      }
    }
  }

  return {
    totalProgramas,
    totalPlanteles: planteles.size,
    totalNiveles: Object.keys(programasEducativos).length,
    totalAreas: Object.keys(estadisticasPorArea).length,
    estadisticasPorNivel,
    estadisticasPorArea,
    planteles: Array.from(planteles).sort(),
  };
}
