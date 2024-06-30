package com.example.vfs.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.*;

@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {
    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        // destination header /topic으로 시작하는 메시지를 기본 Broker로 라우팅
        config.enableSimpleBroker("/topic");
        config.setApplicationDestinationPrefixes("/app");
    }

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        // 클라이언트가 WebSocket Handshake connection을 생성할 Endpoint
        registry.addEndpoint("/signaling")
                .setAllowedOriginPatterns("*")
                .withSockJS();
    }
}
