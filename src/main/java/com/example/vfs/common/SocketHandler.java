package com.example.vfs.common;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.io.*;
import java.net.URL;
import java.util.Base64;

@Slf4j
@Component
public class SocketHandler extends TextWebSocketHandler {

    private static final int FRAME_DELAY_MS = 30;

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        new Thread(() -> {
            try {
                URL url = new URL("http://localhost:5001/video");
                InputStream inputStream = url.openStream();

                ByteArrayOutputStream baos = null;
                boolean inImage = false;
                byte[] buffer = new byte[8192];
                int bytesRead;

                while ((bytesRead = inputStream.read(buffer)) != -1) {
                    for (int i = 0; i < bytesRead; i++) {
                        if (inImage) {
                            if (buffer[i] == (byte) 0xFF && i + 1 < bytesRead && buffer[i + 1] == (byte) 0xD9) {  // JPEG 종료
                                baos.write(buffer, 0, i + 2);
                                byte[] imageBytes = baos.toByteArray();

                                log.info("이미지 생성 완료. 이미지 크기: {} bytes", imageBytes.length);

                                String base64Image = Base64.getEncoder().encodeToString(imageBytes);
                                session.sendMessage(new TextMessage("data:image/jpeg;base64," + base64Image));
                                baos.close();
                                inImage = false;
                                i++;

                                Thread.sleep(FRAME_DELAY_MS);
                                break;
                            } else {
                                baos.write(buffer[i]);
                            }
                        } else if (buffer[i] == (byte) 0xFF && i + 1 < bytesRead && buffer[i + 1] == (byte) 0xD8) {  // JPEG 시작
                            inImage = true;
                            baos = new ByteArrayOutputStream();
                            baos.write(buffer[i]);
                            baos.write(buffer[i + 1]);
                            i++;
                        }
                    }
                }
                inputStream.close();
            } catch (Exception e) {
                log.error(e.getMessage());
            }
        }).start();
    }
}