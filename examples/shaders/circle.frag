#version 150

in vec4 colorFromVertexShader;
in vec4 centerFromVertexShader;

out vec4 outputColor;

uniform vec2 Viewport;
uniform vec2 ViewportOffset;
uniform float Radius;

void main() {
    float x = (centerFromVertexShader.x * Viewport.x / 2.0f) + (Viewport.x / 2.0f) + ViewportOffset.x;
    float y = (centerFromVertexShader.y * Viewport.y / 2.0f) + (Viewport.y / 2.0f) + ViewportOffset.y;

    float d = distance(gl_FragCoord.xy, vec2(x, y));

    float delta = fwidth(d);
    float alpha = smoothstep(Radius-delta, Radius, d);
    outputColor = vec4(colorFromVertexShader.xyz, 1 - alpha);
}