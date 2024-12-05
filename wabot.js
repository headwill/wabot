const { Client } = require('whatsapp-web.js');
const client = new Client();

// Defina sua mensagem de boas-vindas aqui
const welcomeMessageText = `*❁‌፝📖‌፝❁❁‌፝📖‌፝❁👑❁‌፝📖‌፝❁❁‌፝📖‌፝❁*

*_A Paz do Senhor Jesus Cristo !!_*
*_Sejam bem-vindo meu irmão(a) ao GRUPO: ✨💫ADORADORES👑_*

_O nosso grupo já existe há 10 anos, foi fundado dia 10/09/2014, nosso propósito é engradecer o nome santo do Senhor Jesus, com louvores, orações e testemunhos, levando as boas novas, pois "quão formosos são, sobre os montes, os pés do que anuncia as boas novas..." Isaías 52:7._

*_Obrigado por escolher nosso grupo, sentimos honrados por fazer parte dessa igreja virtual._*

*_Adm's_*

  *❁‌፝📖‌፝❁❁‌፝📖‌፝❁👑❁‌፝📖‌፝❁❁‌፝📖‌፝❁*`;

client.on('qr', (qr) => {
    console.log('QR RECEIVED', qr);
});

client.on('ready', () => {
    console.log('Client is ready!');

    // Se você quiser enviar uma mensagem inicial após a autenticação
    // Defina um número e a mensagem que será enviada para esse número.
    // Exemplo: enviar para um número específico
    const number = '1234567890@c.us';  // Substitua pelo seu número
    const message = 'Olá, este é um bot! A autenticação foi concluída.';
    client.sendMessage(number, message);
});

// Captura evento de novos participantes no grupo
client.on('group_join', (notification) => {
    const groupId = notification.chat.id;  // ID do grupo
    const newMembers = notification.users; // Usuários que entraram no grupo

    newMembers.forEach(user => {
        // Envia a mensagem de boas-vindas para o novo participante
        const welcomeMessage = `Olá, @${user}! ${welcomeMessageText}`;
        client.sendMessage(groupId, welcomeMessage);
    });
});

// Responder a mensagens recebidas
client.on('message', message => {
    if (message.body === 'Olá') {
        message.reply('Olá! Como posso ajudar você?');
    }
});

// Inicializa o cliente WhatsApp
client.initialize();