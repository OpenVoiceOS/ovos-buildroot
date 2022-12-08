import QtQuick 2.0
import QtQuick.Layouts 1.2

Canvas {
    id: mycanvas

    property bool inView: true
    property var particles: []

    renderStrategy: Canvas.Threaded
    onPaint: {
        var ctx = getContext("2d");
        ctx.strokeStyle = 'rgba(255,255,255,0.5)';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.clearRect(0, 0, width, height);

        function draw() {
            for (var c = 0; c < particles.length; c++) {
                var p = particles[c];
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p.x, p.y + p.l * p.ys);
                ctx.stroke();
            }
            move();
        }

        function move() {
            for (var b = 0; b < particles.length; b++) {
                var p = particles[b];
                p.y += p.ys;
                if (p.x < 1 || p.x > width || p.y > height) {
                    p.x = Math.random() * width;
                    p.y = -20;
                }
            }
        }
        draw();
    }
    Timer {
        id: animationTimer
        interval: 16
        running: inView
        repeat: true
        onTriggered: parent.requestPaint()
    }

    Component.onCompleted: {
        var init = [];
        var maxParts = 40;
        for (var a = 0; a < maxParts; a++) {
            init.push({
                          x: Math.random() * width,
                          y: Math.random() * height,
                          l: 2 + Math.random() * 2,
                          ys: Math.random() * 10 + 10
                      })
        }

        particles = [];
        for (var b = 0; b < maxParts; b++) {
            particles[b] = init[b];
        }
    }
}
