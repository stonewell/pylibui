#version 150

/* \brief Vertex GLSL shader that demonstrates how to draw basic thick and smooth lines in 3D.
 * This file is a part of shader-3dcurve example (https://github.com/vicrucann/shader-3dcurve).
 *
 * \author Victoria Rudakova
 * \date January 2017
 * \copyright MIT license
*/

uniform mat4 translate;
uniform mat4 scale;

in vec4 Vertex;
in vec4 Color;

out VertexData{
    vec4 mColor;
} VertexOut;

void main(void)
{
    VertexOut.mColor = Color;
    gl_Position = translate * scale * Vertex;
}
