let socket = new WebSocket("ws://localhost:8765");

socket.onopen = function(e) {
    // alert("[open] Connection established");
    // socket.send("My name is John");
};

socket.onmessage = function(event) {
    // alert(`[message] Data received from server: ${event.data}`);
    const response = JSON.parse(event.data);
    if (response.action == "map_data") {
        console.log("map payload", response.payload);
        renderMap(response.payload);
    }

    if (response.action == "frame") {
        renderFrame(response.payload);
    }
};

socket.onclose = function(event) {
    if (event.wasClean) {
        // alert(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
    } else {
        // e.g. server process killed or network down
        // event.code is usually 1006 in this case
        alert('[close] Connection died');
    }
};

socket.onerror = function(error) {
    alert(`[error] ${error.message}`);
};

async function requestFrame(i) {
    const request = {
        action: "request_frame",
        index: i,
    }
    socket.send(JSON.stringify(request));
}
// ---- sockets







var scene = new THREE.Scene();
scene.background = new THREE.Color(0x9ed8ff);
var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

var renderer = new THREE.WebGLRenderer({ antialias: true, autoSize: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

var size = 10;
var divisions = 10;

function drawTriangles2D(triangles_2D) {
    // var roadTexture = new THREE.TextureLoader().load("road.jpg");
    // roadTexture.wrapS = roadTexture.wrapT = THREE.RepeatWrapping;
    // roadTexture.repeat.set(10, 10);
    // // roadTexture.offset.set(10, 200);
    // roadTexture.anisotropy = 5;


    // roadTexture.encoding = THREE.sRGBEncoding;
    // var roadMaterial = new THREE.MeshStandardMaterial({ map: roadTexture });
    // roadMaterial.side = THREE.DoubleSide;

    var roadMaterial = new THREE.MeshPhysicalMaterial({
        color: "#303030",
        reflectivity: 0.0,
        roughness: 1.0,
    });

    var geom = new THREE.Geometry();

    var count = 0;
    for (triangle of triangles_2D) {
        p2 = triangle[0];
        p1 = triangle[1];
        p0 = triangle[2];
        var v1 = new THREE.Vector3(p0[0], 0, p0[1]);
        var v2 = new THREE.Vector3(p1[0], 0, p1[1]);
        var v3 = new THREE.Vector3(p2[0], 0, p2[1]);

        var tri = new THREE.Triangle(v1, v2, v3);
        // var normal = new THREE.Vector3();
        // tri.getNormal(normal);

        geom.vertices.push(tri.a);
        geom.vertices.push(tri.b);
        geom.vertices.push(tri.c);

        geom.faces.push(new THREE.Face3((3 * count + 0), (3 * count + 1), (3 * count + 2)));
        geom.faceVertexUvs[0].push([
            new THREE.Vector2(0.0, 0.0),
            new THREE.Vector2(0.0, 1.0),
            new THREE.Vector2(1.0, 1.0)
        ]);
        count += 1;
    }
    // geom.faceVertexUvs[0].push([new THREE.Vector2(0.0, 0.0),
    //     new THREE.Vector2(0.0, 1.0),
    //     new THREE.Vector2(1.0, 1.0)
    // ]);
    geom.computeFaceNormals();


    // var mesh = new THREE.Mesh(geom, new THREE.MeshBasicMaterial({ color: 0x5a5a5a, side: THREE.DoubleSide }));
    // console.log("ROAD", roadTexture)
    var mesh = new THREE.Mesh(geom, roadMaterial);

    scene.add(mesh);
}

function renderGround() {
    var groundTexture = new THREE.TextureLoader().load("grass.png");
    groundTexture.wrapS = groundTexture.wrapT = THREE.RepeatWrapping;
    // groundTexture.reflectivity = 1.0;
    groundTexture.repeat.set(4000, 4000);
    // groundTexture.offset.set(10, 200);
    groundTexture.anisotropy = 30;
    groundTexture.reflectivity = 1.0
    groundTexture.encoding = THREE.sRGBEncoding;
    groundTexture.rotation.x = 4.0

    var groundMaterial = new THREE.MeshStandardMaterial({ map: groundTexture });
    groundMaterial.side = THREE.DoubleSide;


    var mesh = new THREE.Mesh(new THREE.PlaneBufferGeometry(10000, 10000), groundMaterial);

    mesh.position.y = -0.2;
    mesh.rotation.x = -Math.PI / 2;
    // mesh.receiveShadow = true;
    scene.add(mesh);
}

function renderFrame(frame) {
    var current_frame_agents = {};

    for (agent of frame.agents) {
        current_frame_agents[agent.track_id] = true;
        // console.log("AGENT", agent);
        if (agent.track_id in visible_obstacles) {
            // console.log("move", agent.track_id);
            const a = visible_obstacles[agent.track_id];
            a.position.x = agent.position[0];
            a.position.y = 0.5;
            a.position.z = agent.position[1];
            a.rotation.y = -agent.yaw;

            // console.log("move to", a.position)
        } else {
            // console.log("Create", agent.track_id);
            var geometry = new THREE.BoxGeometry(agent.extent[0] / 2, 2 / 2, agent.extent[1] / 2);
            // var color = new THREE.Color((1 / 255) * agent.color[0], (1 / 255) * agent.color[1], (1 / 255) * agent.color[2]);
            var color = new THREE.Color("rgb(" + agent.color[0] + "," + agent.color[1] + "," + agent.color[2] + ")");

            // console.log(color);
            var material = new THREE.MeshBasicMaterial({
                transparent: true,
                opacity: 0.8,
                // reflectivity: 0.3,

                color: "#" + color.getHexString(),
                // clearcoat: 0.0,
                // transmission: 0.3,
                // metalness: 0.1,
            });
            var cube = new THREE.Mesh(geometry, material);
            cube.rotation.y = -agent.yaw;
            cube.position.x = agent.position[0];
            cube.position.y = 0.5;
            cube.position.z = agent.position[1];
            visible_obstacles[agent.track_id] = cube;
            scene.add(cube);
        }
    }

    for (k in visible_obstacles) {
        // console.log(k);
        // console.log(current_frame_agents);
        // console.log("IN IT?", k in current_frame_agents)
        if (!(k in current_frame_agents)) {
            object = visible_obstacles[k];
            // console.log("Delete", object)
            // object.position.x = 1000;
            scene.remove(object);
            delete visible_obstacles[k];
        }

    }
}

function addSkyDome() {
    // var skyBoxGeometry = new THREE.CubeGeometry(10000, 10000, 10000);
    // var skyBoxMaterial = new THREE.MeshBasicMaterial({ color: 0x9999ff, side: THREE.BackSide });
    // var skyBox = new THREE.Mesh(skyBoxGeometry, skyBoxMaterial);
    // scene.add(skyBox);
    // var skyGeo = new THREE.SphereGeometry(1000, 25, 25);

    // material = new THREE.MeshBasicMaterial({ color: 0x0000ff });
    // var sky = new THREE.Mesh(skyGeo, material);
    // sky.material.side = THREE.BackSide;
    // scene.add(sky);
    scene.fog = new THREE.FogExp2(0x9ed8ff, 0.00055);

}

function addLights() {

    // var light = new THREE.HemisphereLight(0xffffbb, 0x080820, 1.0);
    var light = new THREE.HemisphereLight(0xffffff, 0xffffff, 2.0);

    // light.color.setHSV(0.6, 0.75, 0.5);
    scene.add(light);
    // hemiLight.groundColor.setHSV(0.095, 0.5, 0.5);

    // light.position.set(0, 500, 0);
    // scene.add(light);

    var dirLight = new THREE.DirectionalLight(0xffffff, 0.5);
    dirLight.position.set(-1, 1000, 1000);
    // dirLight.position.multiplyScalar(50);
    dirLight.name = "dirlight";
    dirLight.shadowCameraVisible = true;
    // dirLight.lookAt(0, 0, 0)

    scene.add(dirLight);

    dirLight.castShadow = true;
    dirLight.shadowMapWidth = dirLight.shadowMapHeight = 1024 * 2;

    var d = 300;

    dirLight.shadowCameraLeft = -d;
    dirLight.shadowCameraRight = d;
    dirLight.shadowCameraTop = d;
    dirLight.shadowCameraBottom = -d;

    dirLight.shadowCameraFar = 3500;
    dirLight.shadowBias = -0.0001;
    dirLight.shadowDarkness = 0.35;
}

function renderMap(map_data) {
    console.log("let's render the map", map_data);

    for (way of map_data.ways) {
        if (way.kind == "Virtual") {
            continue;
        } else if (way.kind == "StopLine") {
            renderPolyLine(way.points, 1.0, "#ffffff");
        } else if (way.kind == "ThickLine") {
            renderPolyLine(way.points, 0.1, "#ffffff");
        } else if (way.kind == "SolidLine") {
            renderPolyLine(way.points, 0.05, "#ffffff");
        } else if (way.kind == "RoadBorder") {
            renderPolyLine(way.points, 0.1, "#ffffff");
        } else if (way.kind == "CurbStone") {
            renderPolyLine(way.points, 0.1, "#111111");
        } else if (way.kind == "PedestrianMarking") {
            renderPolyLine(way.points, 1.0, "#999999");
        } else if (way.kind == "DashedLine") {
            renderPolyLine(way.points, 0.1, "#999999");
        }
    }

    for (lane_triangles of map_data.triangulated_lanes) {
        drawTriangles2D(lane_triangles);
    }
}

// Render a polyline by triangulating it.
function renderPolyLine(points, thickness, color) {
    var geom = new THREE.Geometry();

    var material = new THREE.MeshStandardMaterial({
        color: color,
    });

    material.side = THREE.DoubleSide;

    height = 0.1


    for (i = 0; i < points.length - 1; i++) {

        // v1_a                                   v2_a
        // |                                       |
        // |                                       |
        // v1--------------------------------------v2
        // |                                       |
        // |                                       |
        // v1_b                                   v2_b

        var v1 = new THREE.Vector3(points[i][0], 0.0, points[i][1]);
        var v2 = new THREE.Vector3(points[i + 1][0], 0.0, points[i + 1][1]);

        dx = points[i][0] - points[i + 1][0];
        dy = points[i][1] - points[i + 1][1];

        // console.log("DXY", dx, dy)
        var perp_cw = new THREE.Vector3(-dy, 0.0, dx);
        var perp_ccw = new THREE.Vector3(dy, 0.0, -dx);
        perp_cw.normalize();
        perp_ccw.normalize();
        perp_cw.multiplyScalar(thickness / 2);
        perp_ccw.multiplyScalar(thickness / 2);

        // console.log(perp_cw);


        var v1_a = v1.clone().add(perp_ccw);
        var v1_b = v1.clone().add(perp_cw);
        var v2_a = v2.clone().add(perp_ccw);
        var v2_b = v2.clone().add(perp_cw);

        v1_a.y = height;
        v1_b.y = height;
        v2_a.y = height;
        v2_b.y = height;

        geom.vertices.push(v1_a);
        geom.vertices.push(v1_b);
        geom.vertices.push(v2_a);
        geom.vertices.push(v2_b);

        geom.faces.push(new THREE.Face3((4 * i + 2), (4 * i + 1), (4 * i + 0)));
        geom.faces.push(new THREE.Face3((4 * i + 1), (4 * i + 2), (4 * i + 3)));

    }

    geom.computeFaceNormals();
    scene.add(new THREE.Mesh(geom, material));
}

addLights();
addSkyDome();
// light = new THREE.PointLight();
// light.position.set(200, 100, 150);
// scene.add(light);

// var gridHelper = new THREE.GridHelper(400, 40, 0x0000ff, 0x808080);
// gridHelper.position.y = -0.1;
// gridHelper.position.x = 0;
// scene.add(gridHelper);
renderGround();
camera.position.z = 50;
camera.position.y = 50;
camera.position.x = 0;
var point = new THREE.Vector3(50, 0, 50)
camera.lookAt(point);
// camera.up.set(0, 0, 1);

var controls = new THREE.OrbitControls(camera, renderer.domElement);

// map from frame index to Frame object
var visible_obstacles = {};

var current_index = 0;

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
    if (current_index % 5 == 0) {
        requestFrame(current_index / 5);
    }
    current_index += 1;
}

animate();