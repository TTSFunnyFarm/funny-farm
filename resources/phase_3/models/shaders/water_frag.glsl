#version 330

const float DISTORT_STRENGTH = 0.01;

uniform sampler2D p3d_Texture0;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform sampler2D reflectTex;
uniform sampler2D refractTex;
uniform sampler2D dudvMap;
uniform float moveFactor;

in vec4 clipSpace;
in vec2 texCoords;

out vec4 color;
 
void main() {
  vec2 normDev = (clipSpace.xy / clipSpace.w)/2.0 + 0.5;
  vec2 reflectCoords = vec2(normDev.x, -normDev.y);
  vec2 refractCoords = normDev;

  vec2 distortion1 = (texture(dudvMap, vec2(texCoords.x + moveFactor, texCoords.y)).rg * 2.0 - 1.0) * DISTORT_STRENGTH;
  vec2 distortion2 = (texture(dudvMap, vec2(-texCoords.x + moveFactor, texCoords.y + moveFactor)).rg * 2.0 - 1.0) * DISTORT_STRENGTH;
  vec2 distortion = distortion1 + distortion2;

  refractCoords += distortion;
  refractCoords = clamp(refractCoords, 0.001, 0.999);
  reflectCoords += distortion;
  reflectCoords.x = clamp(reflectCoords.x, 0.001, 0.999);
  reflectCoords.y = clamp(reflectCoords.y, -0.999, -0.001);

  vec4 reflectColor = texture(reflectTex, reflectCoords);
  vec4 refractColor = texture(refractTex, refractCoords);

  color = mix(refractColor, reflectColor, 0.15);
  color = mix(color, vec4(0.35, 0.67, 0.95, 1.0), 0.2);
  color.b *= 1.25;
  color.a = 1.0;
}
