#version 400 core

layout(location = 0) in vec3 in_position;
layout(location = 1) in vec2 in_uv;
layout(location = 2) in vec3 in_normal;

out vec3 pass_position;
out vec2 pass_uv;
out vec3 pass_normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

void main(void) {

    vec4 world_pos = model * vec4(in_position, 1.0f);
    gl_Position = proj * view * world_pos;
    
    pass_position = world_pos.xyz;
    pass_uv = in_uv;
    
    vec3 surf_normal = (model * vec4(in_normal, 1.0f)).xyz;
    pass_normal = normalize(surf_normal);

}