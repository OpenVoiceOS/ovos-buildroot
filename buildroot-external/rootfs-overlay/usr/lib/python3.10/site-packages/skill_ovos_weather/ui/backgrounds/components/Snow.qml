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
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        ctx.clearRect(0, 0, width, height);

        function draw() {
            for (var c = 0; c < particles.length; c++) {
                var p = particles[c];
                ctx.beginPath();
                context.arc(p.x, p.y + p.ys, p.l, 0, 2 * Math.PI, false);
                context.fillStyle = Qt.rgba(255,255,255,p.a);
                context.fill();
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
        var maxParts = 80;

        for (var a = 0; a < maxParts; a++) {
            init.push({
                          x: Math.random() * width,
                          y: Math.random() * height,
                          l: 5 + Math.random() * 10,
                          ys: Math.random(),
                          a: 0.4 + Math.random() * 0.6
                      })
        }

        particles = [];
        for (var b = 0; b < maxParts; b++) {
            particles[b] = init[b];
        }
    }
}
