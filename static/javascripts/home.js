$(function () {
    $(window).on('scroll', function () {
        if ( $(window).scrollTop() >= $(window).height() - 15 ) {
            $('.navbar').addClass('active');
						$('.navbar-toggler').removeClass('navbar-dark');
						$('.navbar-toggler').addClass('navbar-light');
        } else {
            $('.navbar').removeClass('active');
						$('.navbar-toggler').removeClass('navbar-light');
						$('.navbar-toggler').addClass('navbar-dark');
        }
    });
});

//宣告全域變數
var scene, camera, renderer;
var geometry, material, mesh;
//定義起始設定函數
function init() {
	//1.建立場景
	scene=new THREE.Scene();
	//2.建立曲面圖形物件
	geometry=new THREE.BoxGeometry(500, 500, 500); //建立幾何形狀
	material=new THREE.MeshBasicMaterial({  //建立材質
		color: 0xffffff,
		wireframe: true});
	mesh=new THREE.Mesh(geometry, material); //以幾何形狀與材質建立曲面
	scene.add(mesh);  //曲面圖形物件加入場景中
	//3.建立相機
	camera=new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 1, 10000);
	camera.position.z=1000;
	//4.建立繪圖器
	renderer=new THREE.WebGLRenderer({canvas: artifactCanvas});  //建立 WebGL 繪圖器
	// renderer.setClearColor("#ffffff");  //設定背景色為白色
	renderer.setSize(100, 50); //設定畫布為瀏覽器大小
	// document.body.appendChild(renderer.domElement); //將畫布加入瀏覽器 DOM 中
	}
//定義動畫函數
function animate() {
	requestAnimationFrame(animate);
	mesh.rotation.x += 0.01;
	mesh.rotation.y += 0.02;
	renderer.render(scene, camera);
	}

window.onload = function() {
	init()
	animate()
}
