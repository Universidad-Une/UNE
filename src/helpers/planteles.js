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


// Función adaptada para planteles sin inscripción con mensualidad variable
function crearPlantelesEspecificos(configuraciones) {
  const planteles = { normal: [], sabatina: [] };
  
  configuraciones.forEach(config => {
    const {
      plantel,
      costoInscripcion = 0,
      costoColegiatura = 0,
      modalidad = 'normal',
      diferentesPrecios = false // Este parámetro no es necesario pero lo mantengo por compatibilidad
    } = config;
    
    const plantelData = {
      nombre: plantel,
      inscripcion: costoInscripcion,
      colegiatura: costoColegiatura
    };
    
    planteles[modalidad].push(plantelData);
  });
  
  return planteles;
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

// OPCIÓN 5: Función para un solo plantel (NUEVA)
function crearPlantelUnico(nombrePlantel, costo, modalidad = 'normal') {
  const planteles = {
    normal: [],
    sabatina: []
  };
  
  planteles[modalidad] = [{
    nombre: nombrePlantel,
    inscripcion: costo,
    colegiatura: costo
  }];
  
  return planteles;
}

// OPCIÓN 6: Función personalizada más flexible (NUEVA)
function crearPlantelPersonalizado(configuracion) {
  const { 
    plantel, 
    costo, 
    modalidad = 'normal',
    diferentesPrecios = false,
    costoInscripcion = null,
    costoColegiatura = null
  } = configuracion;
  
  const planteles = { normal: [], sabatina: [] };
  
  const plantelData = {
    nombre: plantel,
    inscripcion: diferentesPrecios ? costoInscripcion : costo,
    colegiatura: diferentesPrecios ? costoColegiatura : costo
  };
  
  planteles[modalidad].push(plantelData);
  return planteles;
}

// OPCIÓN 7: Función para múltiples planteles con configuración individual (NUEVA)
function crearPlantelesMultiples(configuraciones) {
  const planteles = { normal: [], sabatina: [] };
  
  configuraciones.forEach(config => {
    const {
      plantel,
      costo,
      modalidad = 'normal',
      diferentesPrecios = false,
      costoInscripcion = null,
      costoColegiatura = null
    } = config;
    
    const plantelData = {
      nombre: plantel,
      inscripcion: diferentesPrecios ? costoInscripcion : costo,
      colegiatura: diferentesPrecios ? costoColegiatura : costo
    };
    
    planteles[modalidad].push(plantelData);
  });
  
  return planteles;
}

// OPCIÓN 8: Función para filtrar planteles existentes (NUEVA)
function filtrarPlanteles(planteles, filtros) {
  const { modalidades = ['normal', 'sabatina'], nombresPlantel = [] } = filtros;
  const resultado = {};
  
  modalidades.forEach(modalidad => {
    if (planteles[modalidad]) {
      resultado[modalidad] = nombresPlantel.length > 0 
        ? planteles[modalidad].filter(p => nombresPlantel.includes(p.nombre))
        : planteles[modalidad];
    }
  });
  
  return resultado;
}

// OPCIÓN 9: Función para planteles con diferentes precios por turno
function crearPlantelesConTurnos(configuracion) {
  const {
    modalidad = 'normal',
    planteles = []
  } = configuracion;

  const resultado = { normal: [], sabatina: [] };

  planteles.forEach(plantel => {
    const {
      nombre,
      precioUnico = null,
      precioMatutino = null,
      precioVespertino = null,
      inscripcionUnica = null,
      inscripcionMatutina = null,
      inscripcionVespertina = null
    } = plantel;

    // Si tiene precio único (no varía por turno)
    if (precioUnico) {
      resultado[modalidad].push({
        nombre,
        turno: 'ambos',
        colegiatura: precioUnico,  // ← Cambiar mensualidad por colegiatura
        inscripcion: inscripcionUnica || precioUnico
      });
    }

    // Si tiene precios diferentes por turno
    else if (precioMatutino && precioVespertino) {
      // Crear entrada para matutino
      resultado[modalidad].push({
        nombre: `${nombre} (Matutino)`,
        turno: 'matutino',
        colegiatura: precioMatutino,  // ← Cambiar mensualidad por colegiatura
        inscripcion: inscripcionMatutina || precioMatutino
      });

      // Crear entrada para vespertino
      resultado[modalidad].push({
        nombre: `${nombre} (Vespertino)`,
        turno: 'vespertino',
        colegiatura: precioVespertino,  // ← Cambiar mensualidad por colegiatura
        inscripcion: inscripcionVespertina || precioVespertino
      });
    }
  });

  return resultado;
}



// Exportar funciones para uso
export { 
  crearPlantelesUniformes, 
  crearPlantelesEspecificos, 
  crearPlantelesHibridos,
  crearPlantelesAvanzado,
  crearPlantelUnico,
  crearPlantelPersonalizado,
  crearPlantelesMultiples,
  filtrarPlanteles,
  crearPlantelesConTurnos,
  PLANTELES_NOMBRES 
};


// EJEMPLOS DE USO:

/*
const planteles1 = crearPlantelesUniformes(772, 609);

// Un solo plantel
const planteles2 = crearPlantelUnico("Centro", 850, "normal");

// Plantel con diferentes precios para inscripción y colegiatura
const planteles3 = crearPlantelPersonalizado({
  plantel: "Centro",
  diferentesPrecios: true,
  costoInscripcion: 900,
  costoColegiatura: 800,
  modalidad: "normal"
});

// Múltiples planteles con configuración individual
const planteles4 = crearPlantelesMultiples([
  { plantel: "Centro", costo: 850, modalidad: "normal" },
  { plantel: "Milenio", costo: 750, modalidad: "normal" },
  { plantel: "Tesistán", costo: 680, modalidad: "sabatina" }
]);

// Filtrar planteles específicos
const todosPlanteles = crearPlantelesUniformes(772, 609);
const plantelesGDL = filtrarPlanteles(todosPlanteles, {
  modalidades: ['normal'],
  nombresPlantel: ['Centro', 'Milenio', 'Chapultepec']
});

// Costos específicos por plantel
const planteles5 = crearPlantelesEspecificos({
  normal: {
    "Centro": 850,
    "Milenio": 800,
    "Tesistán": 750
  },
  sabatina: {
    "Centro": 650,
    "Milenio": 600,
    "Tesistán": 550
  }
});
*/