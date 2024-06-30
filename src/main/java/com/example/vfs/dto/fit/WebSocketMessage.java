package com.example.vfs.dto.fit;

import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class WebSocketMessage {
    private String from;
    private String type;
    private String data;
    private Object candidate;
    private Object sdp;

    @Builder
    public WebSocketMessage(String from, String type, String data, Object candidate, Object sdp) {
        this.from = from;
        this.type = type;
        this.data = data;
        this.candidate = candidate;
        this.sdp = sdp;
    }
}