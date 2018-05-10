#version 400 core

in vec3 vcolor;

out vec4 out_color;

void main(void) {
    
    out_color= vec4(vcolor, 1.0f);

}