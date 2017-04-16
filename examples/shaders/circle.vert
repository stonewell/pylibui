#version 150

uniform mat4 translate;
uniform mat4 scale;
in vec4 Vertex;
in vec4 Color;
out vec4 colorFromVertexShader;
out vec4 centerFromVertexShader;
uniform vec2 Center;

void main() {
  gl_Position = translate * scale * Vertex;
  colorFromVertexShader = Color;
  centerFromVertexShader = translate * scale * vec4(Center.xy, 0, 1.0);
}
