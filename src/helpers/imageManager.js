// src/helpers/imageManager.js
// Helper universal para manejar imágenes de todos los niveles educativos

// Importar todas las imágenes de todos los niveles
const allImageModules = {
  licenciaturas: import.meta.glob('/src/assets/Imagenes/CardsLicenciaturas/*.webp', { eager: true }),
  maestrias: import.meta.glob('/src/assets/Imagenes/CardsMaestrias/*.webp', { eager: true }),
  cursos: import.meta.glob('/src/assets/Imagenes/CardsCursos/*.webp', { eager: true }),
  especialidades: import.meta.glob('/src/assets/Imagenes/CardsEspecialidades/*.webp', { eager: true }),
  diplomados: import.meta.glob('/src/assets/Imagenes/CardsDiplomados/*.webp', { eager: true }),
  // Agrega más niveles según necesites (doctorados, especialidades, etc.)
};

// Función universal para obtener URL de imagen
export const getImageUrl = (imageName, nivel = 'licenciaturas') => {
  if (!imageName) {
    return getDefaultImage(nivel);
  }

  const imageModules = allImageModules[nivel];
  if (!imageModules) {
    return getDefaultImage('licenciaturas');
  }

  // Construir la ruta esperada
  const carpetaNivel = `Cards${nivel.charAt(0).toUpperCase() + nivel.slice(1)}`;
  const imagePath = `/src/assets/Imagenes/${carpetaNivel}/${imageName}.webp`;
  const imageModule = imageModules[imagePath];
  
  if (imageModule) {
    const result = imageModule.default || imageModule.src || imageModule;
    // Si es un objeto con propiedad src, extraer solo la URL
    return typeof result === 'object' && result.src ? result.src : result;
  }
  
  // Fallback 1: buscar sin extensión o con nombre similar (case insensitive)
  const similarPath = Object.keys(imageModules).find(path => {
    const fileName = path.split('/').pop().replace('.webp', '').toLowerCase();
    return fileName === imageName.toLowerCase();
  });
  
  if (similarPath) {
    const similarModule = imageModules[similarPath];
    const result = similarModule.default || similarModule.src || similarModule;
    return typeof result === 'object' && result.src ? result.src : result;
  }
  
  // Fallback 2: buscar por coincidencia parcial
  const partialMatch = Object.keys(imageModules).find(path => 
    path.toLowerCase().includes(imageName.toLowerCase()) ||
    imageName.toLowerCase().includes(path.split('/').pop().replace('.webp', '').toLowerCase())
  );
  
  if (partialMatch) {
    const partialModule = imageModules[partialMatch];
    const result = partialModule.default || partialModule.src || partialModule;
    return typeof result === 'object' && result.src ? result.src : result;
  }
  
  return getDefaultImage(nivel);
};

// Función para obtener imagen por defecto
function getDefaultImage(nivel) {
  const imageModules = allImageModules[nivel] || allImageModules.licenciaturas;
  const carpetaNivel = `Cards${nivel.charAt(0).toUpperCase() + nivel.slice(1)}`;
  
  // Intentar obtener imágenes por defecto en orden de prioridad
  const defaultPaths = [
    `/src/assets/Imagenes/${carpetaNivel}/default.webp`,
    `/src/assets/Imagenes/${carpetaNivel}/placeholder.webp`,
    `/src/assets/Imagenes/${carpetaNivel}/no-image.webp`,
    `/src/assets/Imagenes/${carpetaNivel}/sin-imagen.webp`
  ];
  
  for (const defaultPath of defaultPaths) {
    const defaultModule = imageModules[defaultPath];
    if (defaultModule) {
      const result = defaultModule.default || defaultModule.src || defaultModule;
      return typeof result === 'object' && result.src ? result.src : result;
    }
  }
  
  // Último recurso: primera imagen disponible del nivel
  const availableImages = Object.values(imageModules);
  if (availableImages.length > 0) {
    const firstImage = availableImages[0];
    const result = firstImage.default || firstImage.src || firstImage;
    return typeof result === 'object' && result.src ? result.src : result;
  }
  
  // Si todo falla, retorna un data URL básico (SVG placeholder)
  return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI0NSUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0iIzZiNzI4MCI+SW1hZ2VuIG5vIGRpc3BvbmlibGU8L3RleHQ+PHRleHQgeD0iNTAlIiB5PSI2NSUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0iIzliYTFhYiI+SW1hZ2UgTm90IEF2YWlsYWJsZTwvdGV4dD48L3N2Zz4=';
}

// Obtener todas las imágenes disponibles para un nivel
export const getAvailableImages = (nivel) => {
  const imageModules = allImageModules[nivel];
  if (!imageModules) {
    return {};
  }
  
  const images = Object.keys(imageModules).reduce((acc, path) => {
    const imageName = path.split('/').pop().replace('.webp', '');
    const imageModule = imageModules[path];
    const result = imageModule.default || imageModule.src || imageModule;
    acc[imageName] = typeof result === 'object' && result.src ? result.src : result;
    return acc;
  }, {});
  
  return images;
};

// Validar si una imagen existe
export const imageExists = (imageName, nivel) => {
  const imageModules = allImageModules[nivel];
  if (!imageModules) return false;
  
  const carpetaNivel = `Cards${nivel.charAt(0).toUpperCase() + nivel.slice(1)}`;
  const imagePath = `/src/assets/Imagenes/${carpetaNivel}/${imageName}.webp`;
  return !!imageModules[imagePath];
};

// Obtener estadísticas de imágenes
export const getImageStats = () => {
  const stats = {};
  
  Object.keys(allImageModules).forEach(nivel => {
    const imageModules = allImageModules[nivel];
    stats[nivel] = {
      total: Object.keys(imageModules).length,
      images: Object.keys(imageModules).map(path => path.split('/').pop().replace('.webp', ''))
    };
  });
  
  return stats;
};

// Función para validar estructura de carpetas
export const validateImageStructure = () => {
  const report = {
    valid: true,
    issues: [],
    recommendations: []
  };
  
  Object.keys(allImageModules).forEach(nivel => {
    const imageModules = allImageModules[nivel];
    const imageCount = Object.keys(imageModules).length;
    
    if (imageCount === 0) {
      report.valid = false;
      report.issues.push(`No se encontraron imágenes para el nivel: ${nivel}`);
      report.recommendations.push(`Crear carpeta: src/assets/Imagenes/Cards${nivel.charAt(0).toUpperCase() + nivel.slice(1)}/`);
    }
    
    // Verificar si existe imagen por defecto
    const hasDefault = Object.keys(imageModules).some(path => 
      path.includes('default.webp') || path.includes('placeholder.webp')
    );
    
    if (!hasDefault && imageCount > 0) {
      report.recommendations.push(`Agregar imagen por defecto para ${nivel}: default.webp o placeholder.webp`);
    }
  });
  
  return report;
};

// Exportar función helper para usar en componentes
export const createImageUrlGetter = (nivel) => {
  return (imageName) => getImageUrl(imageName, nivel);
};