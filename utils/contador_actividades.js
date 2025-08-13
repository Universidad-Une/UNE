import { actividades } from '../src/helpers/vtuactividades.js';

function normalizarNombre(nombre) {
  return nombre.trim().toLowerCase().replace(/\s+/g, ' ').replace(/\//g, ' / ').replace(/\s+/g, ' ').trim();
}

function obtenerMejorNombre(nombres) {
  return nombres.sort((a, b) => b.length - a.length)[0];
}

function contarActividadesUnicas() {
  const grupos = new Map();
  
  actividades.forEach(actividad => {
    const normalizado = normalizarNombre(actividad.nombre);
    if (!grupos.has(normalizado)) {
      grupos.set(normalizado, []);
    }
    grupos.get(normalizado).push(actividad.nombre);
  });
  
  const nombresUnicos = [];
  grupos.forEach((variantes) => {
    const nombreRepresentativo = obtenerMejorNombre([...new Set(variantes)]);
    nombresUnicos.push(nombreRepresentativo);
  });
  
  nombresUnicos.sort();
  
  console.log(`Total: ${actividades.length}`);
  console.log(`Únicos: ${nombresUnicos.length}`);
  console.log(`Duplicados eliminados: ${actividades.length - nombresUnicos.length}`);
  
  console.log('\nActividades únicas:');
  nombresUnicos.forEach((nombre, index) => {
    console.log(`${index + 1}. ${nombre}`);
  });
  
  return nombresUnicos;
}

contarActividadesUnicas();