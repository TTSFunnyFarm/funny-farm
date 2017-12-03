#version 330

uniform sampler2D p3d_Texture0;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform sampler2D reflectTex;
uniform sampler2D refractTex;

in vec4 clipSpace;
out vec4 color;
 
void main() {
  vec2 normDev = (clipSpace.xy / clipSpace.w)/2.0 + 0.5;
  vec2 reflectCoords = vec2(normDev.x, -normDev.y);
  vec2 refractCoords = normDev;
  vec4 reflectColor = texture(reflectTex, reflectCoords);
  vec4 refractColor = texture(refractTex, refractCoords);
  color = mix(reflectColor, refractColor, 0.5);
}
