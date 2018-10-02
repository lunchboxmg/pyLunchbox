#version 400 core

in vec3 pass_position;
in vec2 pass_uv;
in vec3 pass_normal;

vec3 light_pos = vec3(10.0f, 10.0f, 10.0f);

out vec4 out_color;

uniform sampler2D tex;
uniform vec3 camera_pos;

struct Material {
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float shininess;
};
uniform Material material;

struct Light {
    vec4 position;
    vec3 direction;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float constant;
    float linear;
    float quadratic;
};
uniform Light lights;

vec3 calc_light(Light light, vec3 dir_view) {

    vec3 dir_light;
    if (light.position.w == 0) {
        dir_light = normalize(light.position.xyz - pass_position);
    } else { 
        dir_light = normalize(light.direction);
    }
    vec3 dir_reflect = reflect(-dir_light, pass_normal);
  
    float diff = max(dot(pass_normal, dir_light), 0.0f);
    float spec = pow(max(dot(dir_view, dir_reflect), 0.0f), material.shininess);

    //vec3 ambient  = light.ambient  *        vec3(texture(material.diffuse, pass_uv));
    //vec3 diffuse =  light.diffuse  * diff * vec3(texture(material.diffuse, pass_uv));
    //vec3 specular = light.specular * spec * vec3(texture(material.specular, pass_uv));
    
    vec3 ambient  = light.ambient * material.ambient;
    vec3 diffuse = light.diffuse * (diff * material.diffuse);
    vec3 specular = light.specular * (spec * material.specular);

    float dist = length(light.position.xyz - pass_position);
    float attn = 1.0f / (light.constant + light.linear * dist + 
                         light.quadratic * (dist * dist));
    
    return (ambient + diffuse + specular) * attn;
}

void main(void) {


    // Setup vectors ...    
    vec3 normal = pass_normal;
    vec3 L = normalize(light_pos - pass_position); // light direction
    vec3 E = normalize(-pass_position);
    vec3 R = normalize(-reflect(L, normal));
    vec3 dir_view = normalize(camera_pos - pass_position);
    
    float alpha = dot(normal, L);
    float brightness = max(alpha, 0.3f);
    vec3 diffuse = brightness * vec3(1.0f, 1.0f, 1.0f);
    
    vec4 px_color = vec4(1.0f, 1.0f, 1.0f, 1.0f);
    vec4 color_tex = texture(tex, pass_uv);
    out_color = vec4(diffuse, 1.0f) * px_color * color_tex;

}