#version 400 core

in vec3 position;
in vec2 uv;
in vec3 normal;

out vec3 vcolor;

uniform mat4 model;
uniform mat4 proj;
uniform mat4 view;

void main(void) {

    vec4 pos_world = model * vec4(position, 1.0f);
    gl_Position = proj * view * pos_world;
    
    vcolor = vec3(1.0f, 1.0f, 1.0f);
}