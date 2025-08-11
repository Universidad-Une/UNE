import https from 'https';
import { URL } from 'url';

// Configuración de la petición
const apiUrl = 'https:/intranet.universidad-une.com/api/v2/custom/une_create_crm';
const headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic b3NjYXIubXVyb0B4bWFydHMuY29tOkxlZHhPc2Nhck11cm8='
};

const requestData = {
    "nombre": "Test-node",
    "apellido_p": "Casares",
    "apellido_m": "Rojas",
    "correo": "test-api@xmarts.com",
    "nivel_educativo": "Bachillerato",
    "plantel_interes": "Sec. Mix. 7",
    "programa_interes": "Derecho",
    "telefono": "1264852555",
    "modalidad": "Mañanera"
};

console.log('=== INICIANDO PETICIÓN API ===');
console.log('🔗 URL:', apiUrl);
console.log('📋 Headers enviados:');
Object.entries(headers).forEach(([key, value]) => {
    console.log(`   ${key}: ${value}`);
});
console.log('📦 Datos a enviar:');
console.log(JSON.stringify(requestData, null, 2));
console.log('==========================================\n');

// Parsear la URL
const url = new URL(apiUrl);
const postData = JSON.stringify(requestData);

// Configuración de la petición
const options = {
    hostname: url.hostname,
    port: 443,
    path: url.pathname,
    method: 'POST',
    headers: {
        ...headers,
        'Content-Length': Buffer.byteLength(postData)
    }
};

console.log('🚀 Enviando petición...');
console.log('⏱️  Timestamp:', new Date().toISOString());

// Realizar la petición
const req = https.request(options, (res) => {
    console.log('\n=== RESPUESTA RECIBIDA ===');
    console.log('📊 Status Code:', res.statusCode);
    console.log('📊 Status Message:', res.statusMessage);
    
    console.log('📋 Headers de respuesta:');
    Object.entries(res.headers).forEach(([key, value]) => {
        console.log(`   ${key}: ${value}`);
    });
    
    let responseBody = '';
    
    res.on('data', (chunk) => {
        responseBody += chunk;
        console.log('📥 Chunk recibido:', chunk.length, 'bytes');
    });
    
    res.on('end', () => {
        console.log('\n=== RESPUESTA COMPLETA ===');
        console.log('📦 Body de respuesta:');
        
        try {
            // Intentar parsear como JSON
            const jsonResponse = JSON.parse(responseBody);
            console.log(JSON.stringify(jsonResponse, null, 2));
        } catch (error) {
            console.log('⚠️  La respuesta no es JSON válido, mostrando como texto:');
            console.log(responseBody);
        }
        
        console.log('\n=== RESUMEN ===');
        console.log('✅ Petición completada exitosamente');
        console.log('📊 Status:', res.statusCode);
        console.log('📏 Tamaño de respuesta:', responseBody.length, 'caracteres');
        console.log('⏱️  Finalizado:', new Date().toISOString());
    });
});

// Manejo de errores de la petición
req.on('error', (error) => {
    console.error('\n❌ ERROR EN LA PETICIÓN:');
    console.error('🔥 Mensaje:', error.message);
    console.error('🔥 Code:', error.code);
    console.error('🔥 Stack trace:');
    console.error(error.stack);
    
    if (error.code === 'ENOTFOUND') {
        console.error('💡 Posible causa: Problema de DNS o conectividad');
    } else if (error.code === 'ECONNREFUSED') {
        console.error('💡 Posible causa: Servidor no disponible');
    } else if (error.code === 'ETIMEDOUT') {
        console.error('💡 Posible causa: Timeout de conexión');
    }
});

// Manejo de timeout
req.setTimeout(30000, () => {
    console.error('\n⏰ TIMEOUT: La petición tardó más de 30 segundos');
    req.destroy();
});

// Enviar los datos
console.log('📤 Escribiendo datos al stream...');
req.write(postData);
console.log('✅ Datos escritos, cerrando conexión...');
req.end();

// Logging adicional para debugging
process.on('uncaughtException', (error) => {
    console.error('\n🚨 EXCEPCIÓN NO CAPTURADA:');
    console.error(error);
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('\n🚨 PROMISE REJECTION NO MANEJADA:');
    console.error('Reason:', reason);
    console.error('Promise:', promise);
});