#version 400 core

in vec2 pass_uv;
in vec3 pass_color;
in vec3 surf_normal;
in vec3 to_light;

uniform sampler2D tex;

out vec4 out_color;

void main(void) {
    
    vec3 unit_normal = normalize(surf_normal);
    vec3 unit_to_light = normalize(to_light);
    
    float alpha = dot(unit_normal, unit_to_light);
    float brightness = max(alpha, 0.25f);
    vec3 diffuse = brightness * vec3(1.0f, 1.0f, 1.0f);
    
    vec4 color_tex = texture(tex, pass_uv);
    out_color = vec4(diffuse, 1.0f) * vec4(pass_color, 1.0f) * color_tex;

}