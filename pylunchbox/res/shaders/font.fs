#version 330

in vec2 pass_uv;

out vec4 out_color;

uniform sampler2D tex;
uniform vec3 color;
uniform vec3 outline_color;

// For large font, use low edge value, slightly higher width
// For small font, use high edge value, slightly lower width
const float width = 0.5;
const float edge = 0.1;

// for glow, increase edge, lower width
const float border_width = 0.7; // set to zero for no outline
const float border_edge = 0.1;

// for shadow
const vec2 offset = vec2(0.00, 0.00); // set to zero for no shadow

void main(void) {

    // How far away from the outer edge of the distance field
    float dist = 1.0f - texture(tex, pass_uv).a;
    float alpha = 1.0f - smoothstep(width, width + edge, dist);

    float dist2 = 1.0f - texture(tex, pass_uv + offset).a;
    float alpha_outline = 1.0f - smoothstep(border_width, border_width + border_edge, dist2);

    float alpha_total = alpha + (1.0f - alpha) * alpha_outline;
    vec3 color_total = mix(outline_color, color, alpha / alpha_total);

    out_color = vec4(color_total, alpha_total);
}