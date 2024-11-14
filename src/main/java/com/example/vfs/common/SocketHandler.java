package com.example.vfs.common;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Base64;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Component
public class SocketHandler extends TextWebSocketHandler {

    private final Map<String, StringBuilder> sessionData = new ConcurrentHashMap<>();
    private final Map<String, Integer> sessionChunkCount = new ConcurrentHashMap<>();

    @Override
    public void handleTextMessage(WebSocketSession session, TextMessage message) {
        try {
            String payload = message.getPayload();
            Map<String, Object> data = parsePayload(payload);

            String chunk = (String) data.get("chunk");
            int chunkIndex = (int) data.get("chunkIndex");
            int totalChunks = (int) data.get("totalChunks");

            sessionData.computeIfAbsent(session.getId(), k -> new StringBuilder()).append(chunk);
            sessionChunkCount.put(session.getId(), sessionChunkCount.getOrDefault(session.getId(), 0) + 1);

            if (sessionChunkCount.get(session.getId()) == totalChunks) {
                processCompleteImage(session);
                sessionData.remove(session.getId());
                sessionChunkCount.remove(session.getId());
            }

        } catch (Exception e) {
            log.error("Error in handling message: ", e);
        }
    }

    private void processCompleteImage(WebSocketSession session) {
        try {
            String base64Image = sessionData.get(session.getId()).toString();
            byte[] imageBytes = Base64.getDecoder().decode(base64Image);

            URL url = new URL("http://flask-app:5001/process_frame");
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setDoOutput(true);
            connection.setRequestProperty("Content-Type", "application/octet-stream");

            try (OutputStream outputStream = connection.getOutputStream()) {
                outputStream.write(imageBytes);
            }

            InputStream inputStream = connection.getInputStream();
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            byte[] buffer = new byte[8192];
            int read;
            while ((read = inputStream.read(buffer)) != -1) {
                baos.write(buffer, 0, read);
            }

            String processedBase64Image = baos.toString("UTF-8");
            session.sendMessage(new TextMessage(processedBase64Image));
        } catch (Exception e) {
            log.error("Error in processing complete image: ", e);
        }
    }

    private Map<String, Object> parsePayload(String payload) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            return mapper.readValue(payload, new TypeReference<Map<String, Object>>() {});
        } catch (JsonProcessingException e) {
            log.error("Error parsing JSON payload: ", e);
            return null; // 오류 발생 시 null 반환
        }
    }

//    private static final int FRAME_DELAY_MS = 30;
//
//    @Override
//    public void afterConnectionEstablished(WebSocketSession session) {
//        new Thread(() -> {
//            try {
//                URL url = new URL("http://localhost:5001/video");
//                InputStream inputStream = url.openStream();
//
//                ByteArrayOutputStream baos = null;
//                boolean inImage = false;
//                byte[] buffer = new byte[8192];
//                int bytesRead;
//
//                while ((bytesRead = inputStream.read(buffer)) != -1) {
//                    for (int i = 0; i < bytesRead; i++) {
//                        if (inImage) {
//                            if (buffer[i] == (byte) 0xFF && i + 1 < bytesRead && buffer[i + 1] == (byte) 0xD9) {  // JPEG 종료
//                                baos.write(buffer, 0, i + 2);
//                                byte[] imageBytes = baos.toByteArray();
//
//                                log.info("이미지 생성 완료. 이미지 크기: {} bytes", imageBytes.length);
//
//                                String base64Image = Base64.getEncoder().encodeToString(imageBytes);
//                                session.sendMessage(new TextMessage("data:image/jpeg;base64," + base64Image));
//                                baos.close();
//                                inImage = false;
//                                i++;
//
//                                Thread.sleep(FRAME_DELAY_MS);
//                                break;
//                            } else {
//                                baos.write(buffer[i]);
//                            }
//                        } else if (buffer[i] == (byte) 0xFF && i + 1 < bytesRead && buffer[i + 1] == (byte) 0xD8) {  // JPEG 시작
//                            inImage = true;
//                            baos = new ByteArrayOutputStream();
//                            baos.write(buffer[i]);
//                            baos.write(buffer[i + 1]);
//                            i++;
//                        }
//                    }
//                }
//                inputStream.close();
//            } catch (Exception e) {
//                log.error(e.getMessage());
//            }
//        }).start();
//    }
}