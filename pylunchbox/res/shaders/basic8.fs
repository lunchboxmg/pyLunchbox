#version 400 core

in vec3 vcolor;
in vec3 surf_normal;
in vec3 to_light;

out vec4 out_color;

void main(void) {
    
    vec3 unit_normal = normalize(surf_normal);
    vec3 unit_to_light = normalize(to_light);
    
    float alpha = dot(unit_normal, unit_to_light);
    float brightness = max(alpha, 0.1f);
    vec3 diffuse = brightness * vec3(1.0f, 1.0f, 1.0f);
    
    out_color = vec4(diffuse, 1.0f) * vec4(vcolor, 1.0f);

}