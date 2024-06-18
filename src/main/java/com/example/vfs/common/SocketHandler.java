package com.example.vfs.common;

import com.example.vfs.dto.fit.WebSocketMessage;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.util.Base64;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

@Slf4j
@Component
public class SocketHandler extends TextWebSocketHandler {
    List<WebSocketSession> sessions = new CopyOnWriteArrayList<>();

    private final ObjectMapper objectMapper = new ObjectMapper();
    private static final String MSG_TYPE_JOIN = "join";
    private static final String MSG_TYPE_LEAVE = "leave";

    // 소켓 연결되었을 때, 이벤트 처리
    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        try {
            WebSocketMessage webSocketMessage = WebSocketMessage.builder()
                    .from("Server")
                    .type(MSG_TYPE_JOIN)
                    .data(null)
                    .candidate(null)
                    .sdp(null)
                    .build();
            String json = objectMapper.writeValueAsString(webSocketMessage);
            session.sendMessage(new TextMessage(json));
            sessions.add(session);
        } catch (IOException e) {
            log.error("An error occured: {}", e.getMessage());
        }
    }

    // 소켓 연결이 닫혔을 때, 이벤트 처리
    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws IOException {
        log.info("[ws] Session has been closed with status [{} {}]", status, session);
        WebSocketMessage webSocketMessage = WebSocketMessage.builder()
                .from("Server")
                .type(MSG_TYPE_LEAVE)
                .data(null)
                .candidate(null)
                .sdp(null)
                .build();
        String json = objectMapper.writeValueAsString(webSocketMessage);
        session.sendMessage(new TextMessage(json));
        sessions.remove(session);
    }

    // 소켓 메세지 처리
    @Override
    public void handleTextMessage(WebSocketSession session, TextMessage textMessage) throws IOException {
        try {
            WebSocketMessage message = objectMapper.readValue(textMessage.getPayload(), WebSocketMessage.class);
            log.info("[ws] Message of {} type from {} received", message.getFrom(), message.getType());

            switch (message.getType()) {
                case MSG_TYPE_JOIN:
                    log.info("[ws] {id] has joined Room");
                    /*
                    new Thread(() -> {
                        try {
                            URL url = new URL("http://localhost:5000/video");
                            InputStream is = url.openStream();
                            ByteArrayOutputStream baos = new ByteArrayOutputStream();
                            byte[] buffer = new byte[1024];
                            int bytesRead;

                            while ((bytesRead = is.read(buffer)) != -1) {
                                baos.write(buffer, 0, bytesRead);
                                String base64Image = Base64.getEncoder().encodeToString(baos.toByteArray());
                                session.sendMessage(new TextMessage(base64Image));
                                baos.reset();
                            }

                            is.close();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }).start();
                    */
                    break;
                case MSG_TYPE_LEAVE:
                    log.info("[ws] {id} is going to leave Room");
                    break;
                    // 프로세스 추가 예정
                default:
                    log.info("[ws] Type of the received message {} is undefined!", message.getType());
            }
        } catch (IOException e) {
            log.error("An error occured: {}", e.getMessage());
        }
    }
}
