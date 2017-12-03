#version 330

const float TEXTURE_SCALE = 6.0;

uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform vec3 cameraPos;

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec4 clipSpace;
out vec2 texCoords;

void main() {
  clipSpace = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  texCoords = p3d_MultiTexCoord0 * TEXTURE_SCALE;
  gl_Position = clipSpace;
}
