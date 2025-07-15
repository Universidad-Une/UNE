// Lista de planteles base
const PLANTELES_NOMBRES = [
  "Milenio",
  "Centro", 
  "Centro Médico",
  "Tesistán",
  "Tlajomulco",
  "Tlaquepaque",
  "Tonalá",
  "Chapultepec",
  "Zapopan"
];

// OPCIÓN 1: Función para costos uniformes (todos iguales por modalidad)
function crearPlantelesUniformes(costoNormal, costoSabatina) {
  return {
    normal: PLANTELES_NOMBRES.map(nombre => ({
      nombre,
      inscripcion: costoNormal,
      colegiatura: costoNormal
    })),
    sabatina: PLANTELES_NOMBRES.map(nombre => ({
      nombre,
      inscripcion: costoSabatina,
      colegiatura: costoSabatina
    }))
  };
}

// OPCIÓN 2: Función para costos específicos por plantel
function crearPlantelesEspecificos(costosEspecificos) {
  return {
    normal: PLANTELES_NOMBRES.map(nombre => ({
      nombre,
      inscripcion: costosEspecificos.normal[nombre] || 0,
      colegiatura: costosEspecificos.normal[nombre] || 0
    })),
    sabatina: PLANTELES_NOMBRES.map(nombre => ({
      nombre,
      inscripcion: costosEspecificos.sabatina[nombre] || 0,
      colegiatura: costosEspecificos.sabatina[nombre] || 0
    }))
  };
}

// OPCIÓN 3: Función híbrida (algunos uniformes, otros específicos)
function crearPlantelesHibridos(configuracion) {
  const { 
    costosUniformes, 
    costosEspecificos = {}, 
    modalidades = ['normal', 'sabatina'] 
  } = configuracion;

  const resultado = {};

  modalidades.forEach(modalidad => {
    resultado[modalidad] = PLANTELES_NOMBRES.map(nombre => {
      // Si hay costo específico para este plantel, usarlo
      if (costosEspecificos[modalidad]?.[nombre]) {
        return {
          nombre,
          inscripcion: costosEspecificos[modalidad][nombre],
          colegiatura: costosEspecificos[modalidad][nombre]
        };
      }
      // Si no, usar el costo uniforme
      return {
        nombre,
        inscripcion: costosUniformes[modalidad],
        colegiatura: costosUniformes[modalidad]
      };
    });
  });

  return resultado;
}

// EJEMPLOS DE USO:





// OPCIÓN 4: Función más avanzada con validaciones
function crearPlantelesAvanzado(config) {
  const { 
    tipo = 'uniforme', 
    costosNormal = 772, 
    costosSabatina = 609,
    costosPersonalizados = {},
    validarCostos = true
  } = config;

  // Validaciones
  if (validarCostos) {
    if (tipo === 'uniforme' && (!costosNormal || !costosSabatina)) {
      throw new Error('Para tipo uniforme, se requieren costosNormal y costosSabatina');
    }
    if (tipo === 'personalizado' && Object.keys(costosPersonalizados).length === 0) {
      throw new Error('Para tipo personalizado, se requieren costosPersonalizados');
    }
  }

  if (tipo === 'uniforme') {
    return crearPlantelesUniformes(costosNormal, costosSabatina);
  } else if (tipo === 'personalizado') {
    return crearPlantelesEspecificos(costosPersonalizados);
  }

  return {};
}

// Exportar funciones para uso
export { 
  crearPlantelesUniformes, 
  crearPlantelesEspecificos, 
  crearPlantelesHibridos,
  crearPlantelesAvanzado,
  PLANTELES_NOMBRES 
};