#version 330

layout(location=0) in vec2 in_position;
layout(location=1) in vec2 in_uv;

out vec2 pass_uv;

uniform vec3 transform;

void main(void) {

    vec2 screen_pos = in_position * transform.z + transform.xy;
    screen_pos.x = 2.0f * screen_pos.x - 1.0f;
    screen_pos.y = 1.0f - 2.0f * screen_pos.y;
    gl_Position = vec4(screen_pos, 0.0f, 1.0f);

    pass_uv = in_uv;
}
