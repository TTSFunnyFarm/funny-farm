#version 330

uniform mat4 p3d_ModelViewProjectionMatrix;

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec4 clipSpace;

void main() {
  clipSpace = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  gl_Position = clipSpace;
}
