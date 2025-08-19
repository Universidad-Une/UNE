// src/helpers/imageMap.js
import PuertoVallarta from "../assets/Imagenes/CardsPlanteles/PuertoVallarta.webp";
import CampusPuertoVallarta from "../assets/Imagenes/CardsPlanteles/Campus-Puerto-Vallarta.webp";
import PlazaSol from "../assets/Imagenes/CardsPlanteles/PlazaSol.webp";
import Tesistan from "../assets/Imagenes/CardsPlanteles/Tesistan.webp";
import Tlajomulco from "../assets/Imagenes/CardsPlanteles/Tlajomulco.webp";
import Tlaquepaque from "../assets/Imagenes/CardsPlanteles/Tlaquepaque.webp";
import Tonala from "../assets/Imagenes/CardsPlanteles/Tonala.webp";
import Caracol from "../assets/Imagenes/CardsPlanteles/Caracol.webp";
import Centro from "../assets/Imagenes/CardsPlanteles/Centro.webp";
import CentroMedico from "../assets/Imagenes/CardsPlanteles/CentroMedico.webp";
import Chapultepec from "../assets/Imagenes/CardsPlanteles/Chapultepec.webp";
import LasJuntas from "../assets/Imagenes/CardsPlanteles/lasjuntas.webp";
import Milenio from "../assets/Imagenes/CardsPlanteles/Milenio.webp";
import Tepatitlan from "../assets/Imagenes/CardsPlanteles/Tepatitlan.webp";
import TorreMillenio from "../assets/Imagenes/CardsPlanteles/Torre-milenio.webp";
import TorreQuetzal from "../assets/Imagenes/CardsPlanteles/Torre-quetzal.webp";
import Zapopan from "../assets/Imagenes/CardsPlanteles/Zapopan.webp";

export const imageMap = {
  "PuertoVallarta": PuertoVallarta.src,
  "CampusPuertoVallarta": CampusPuertoVallarta.src,
  "PlazaSol": PlazaSol.src,
  "Tesistan": Tesistan.src,
  "Tlajomulco": Tlajomulco.src,
  "Tlaquepaque": Tlaquepaque.src,
  "Tonala": Tonala.src,
  "Caracol": Caracol.src,
  "Centro": Centro.src,
  "CentroMedico": CentroMedico.src,
  "Chapultepec": Chapultepec.src,
  "LasJuntas": LasJuntas.src,
  "Milenio": Milenio.src,
  "Tepatitlan": Tepatitlan.src,
  "TorreMillenio": TorreMillenio.src,
  "TorreQuetzal": TorreQuetzal.src,
  "Zapopan": Zapopan.src,
};

// Función helper para obtener la imagen
export const getImageById = (id) => {
  const imageKeys = {
    // IDs originales
    "1": "PuertoVallarta",
    "2": "PlazaSol", 
    "3": "Tesistan",
    "4": "Tlajomulco",
    "5": "Tlaquepaque",
    "6": "Tonala",
    
    // Nuevos IDs para planteles adicionales
    "7": "CampusPuertoVallarta",
    "8": "Caracol",
    "9": "Centro",
    "10": "CentroMedico",
    "11": "Chapultepec",
    "12": "LasJuntas",
    "13": "Milenio",
    "14": "Tepatitlan",
    "15": "TorreMillenio",
    "16": "TorreQuetzal",
    "17": "Zapopan",
  };
  
  const imageKey = imageKeys[id];
  const imageSrc = imageMap[imageKey];
  
  return imageSrc || null;
};

// Función helper alternativa para obtener imagen por nombre de archivo
export const getImageByName = (imageName) => {
  return imageMap[imageName] || null;
};

// Función helper para obtener imagen por nombre de plantel (más intuitivo)
export const getImageByPlantelName = (plantelName) => {
  const plantelMap = {
    // Mapeo por nombres comunes de planteles
    "avenida-mexico": "PuertoVallarta",
    "puerto-vallarta": "PuertoVallarta",
    "campus-puerto-vallarta": "CampusPuertoVallarta",
    "plaza-del-sol": "PlazaSol",
    "tesistan": "Tesistan",
    "tlajomulco": "Tlajomulco",
    "tlaquepaque": "Tlaquepaque",
    "tonala": "Tonala",
    "caracol": "Caracol",
    "centro": "Centro",
    "centro-medico": "CentroMedico",
    "chapultepec": "Chapultepec",
    "las-juntas": "LasJuntas",
    "milenio": "Milenio",
    "tepatitlan": "Tepatitlan",
    "torre-milenio": "TorreMillenio",
    "torre-quetzal": "TorreQuetzal",
    "zapopan": "Zapopan",
  };
  
  const imageKey = plantelMap[plantelName.toLowerCase()];
  return imageMap[imageKey] || null;
};