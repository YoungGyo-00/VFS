package com.example.vfs.controller;

import com.example.vfs.common.ApiResponse;
import com.example.vfs.dto.video.request.VideoRequestDto;
import com.example.vfs.service.VideoService;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/video")
public class VideoController {

    private final VideoService videoService;

    @Operation(summary = "실시간 비디오 만들기")
    @PostMapping("/")
    public ApiResponse createVideo(@RequestBody VideoRequestDto videoRequestDto) throws IOException {
        videoService.imagesToVideo(videoRequestDto);
        return ApiResponse.successWithNoContent();
    }
}
