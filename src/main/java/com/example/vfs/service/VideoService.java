package com.example.vfs.service;

import com.example.vfs.dto.video.request.VideoRequestDto;
import lombok.RequiredArgsConstructor;
import net.bramp.ffmpeg.FFmpeg;
import net.bramp.ffmpeg.FFmpegExecutor;
import net.bramp.ffmpeg.builder.FFmpegBuilder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class VideoService {
    private final FFmpeg ffmpeg;
    private static String outputPath = "data/video/output.mp4";
    
    public void imagesToVideo(VideoRequestDto videoRequestDto) throws IOException {
        String inputPath = videoRequestDto.getFilePath();
        String inputPattern = inputPath + "/%d.jpg"; // 1.jpg, 2.jpg 등 순차적 이미지 파일 패턴

        System.out.println("Input Path: " + inputPath);
        System.out.println("Input Pattern: " + inputPattern);

        // 입력 경로에 파일이 존재하는지 확인
        if (!Files.exists(Paths.get(inputPath))) {
            throw new IOException("Input path does not exist: " + inputPath);
        }

        try {
            FFmpegBuilder builder = new FFmpegBuilder()
                    .setInput(inputPattern) // 이미지 파일 입력 경로
                    .addExtraArgs("-framerate", "30") // 프레임 레이트 설정
                    .overrideOutputFiles(true) // 기존 파일 덮어쓰기
                    .addOutput(outputPath) // 출력 경로
                    .setVideoCodec("libx264") // 비디오 코덱
                    .setVideoResolution(1280, 720) // 해상도
                    .setStrict(FFmpegBuilder.Strict.EXPERIMENTAL) // 실험적인 옵션 허용
                    .done();

            FFmpegExecutor executor = new FFmpegExecutor(ffmpeg);
            executor.createJob(builder).run();
        } catch (Exception e) {
            System.out.println(e);
        }
        return;
    }
}
