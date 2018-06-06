#version 330

in vec2 pass_uv;

out vec4 out_color;

uniform sampler2D tex;
uniform vec3 color;

void main(void) {

    float alpha = texture(tex, pass_uv);
    out_color = vec4(color, alpha);
}