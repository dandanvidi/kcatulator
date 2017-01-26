<!DOCTYPE html>
<html lang="en" ng-app>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="">
  <meta name="author" content="">
  <title>kcatulator</title>
  <link href="css/animate.min.css" rel="stylesheet"> 
  <link href="css/font-awesome.min.css" rel="stylesheet">
  <link href="css/lightbox.css" rel="stylesheet">
  <link href="css/main.css" rel="stylesheet">
  <link id="css-preset" href="css/presets/preset1.css" rel="stylesheet">
  <link href="css/responsive.css" rel="stylesheet">
        <link href="assets/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
  
        <script src="assets/js/jquery.mockjax.js"></script>
        <script src="src/bootstrap-typeahead.js"></script>

  <!--[if lt IE 9]>
    <script src="js/html5shiv.js"></script>
    <script src="js/respond.min.js"></script>
  <![endif]-->
  
  <link href='http://fonts.googleapis.com/css?family=Open+Sans:300,400,600,700' rel='stylesheet' type='text/css'>
  <link rel="shortcut icon" href="images/favicon.ico">
  

  <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.6.0/angular.min.js"></script>
	<script src="src/Chart.bundle.min.js"></script>


</head><!--/head-->

<body>

  <!--.preloader-->
  <div class="preloader"> <i class="fa fa-circle-o-notch fa-spin"></i></div>
  <!--/.preloader-->
 
    <div id="contact-us">
      <div class="container">
        <div class="row">
          <div class="heading text-center col-sm-6 col-sm-offset-3 wow fadeInUp" data-wow-duration="1000ms" data-wow-delay="300ms">
            <h2>kcatulator</h2><br><br>
            <input id="demo1" type="text" class="col-sm-12 typeahead tt-query my-form-control" placeholder="Type a name of an enzyme..." autocomplete="off" />
          </div>
        </div>
      </div>
    </div>        
 
 
 
	<div class="row reactions">
    <div id="list" class="container-fluid ">
      <div class="heading wow fadeInUp " data-wow-duration="1000ms" data-wow-delay="300ms">
          <div class="text-center col-sm-6 col-sm-offset-3">
						<ul id="reactions" class="list-group" style="padding-top:20px;">
						</ul>
          </div>
        </div> 
      </div>
    </div>

<section id="graphs">
	<div class="container pricing-table">
		<div class="heading text-center col-sm-8 col-sm-offset-2" wow fadeInUp" data-wow-duration="1200ms" data-wow-delay="300ms">
					<canvas class="single-table" id="canvas" ></canvas>
		</div>
	</div>
	</section>
 
 
 
  <footer id="footer">
    <div class="footer-top wow fadeInUp" data-wow-duration="1000ms" data-wow-delay="300ms">
      <div class="container text-center">
        <div class="footer-logo">
          <a href="index.html"><img class="img-responsive" src="" alt=""></a>
        </div>
        <div class="social-icons">
            <a class="envelope" href="#"><i class="fa fa-envelope"></i></a>
            <a class="twitter" href="#"><i class="fa fa-twitter"></i></a>
            <a class="dribbble" href="#"><i class="fa fa-dribbble"></i></a>
            <a class="facebook" href="#"><i class="fa fa-facebook"></i></a>
            <a class="linkedin" href="#"><i class="fa fa-linkedin"></i></a>
            <a class="tumblr" href="#"><i class="fa fa-tumblr-square"></i></a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="container">
        <div class="row">
          <div class="col-sm-12 text-center">
            <p>&copy; 2016 kcatulator.</p>
          </div>
          <div class="col-sm-6">
            <p class="pull-right"></p>
          </div>
        </div>
      </div>
    </div>
  </footer>


  <script>
		var gene;
			$(function() {
				$.post("GetGenes.php", function(data, status){
				  var sor = JSON.parse(data);
				  
				  function displayResult(item) {
						gene = item.value.substr(0,item.value.lastIndexOf('-') - 1);
						$.post("GetReactions.php", {data: gene}, function(result, status){
					    var res = JSON.parse(result);
					    $('#reactions').empty();
					    for (var i = 0; i < res.length; i++) {
								var reaction = res[i].substr(0,res[i].lastIndexOf('-') - 1);
						    $('#reactions').append("<li class='list-group-item' id='" + reaction + "'>" + res[i] + "</li>");
							}
						  $("#list").show();		
					   $("#graphs").hide();
						});
				  }
				  
				  $('#demo1').typeahead({
				      source: sor,
				      onSelect: displayResult
				  });
			});
		});
          
      
			$('ul').on('click', 'li', function() {
		    var reaction = $(this).text();
		    reaction = reaction.substr(0,reaction.lastIndexOf('-') - 1);					    

				$('li').css('background-color', '#fff');
				$('#' + reaction).css('background-color', '#00BFFF');

		    $.post("GetGraphs.php", {data: gene, reaction: reaction}, function(graph_data, status){
			        var data = JSON.parse(graph_data);
			        data = JSON.parse(data[0]);
			        
			        var acetate = parseFloat(data.acetate);
			        var pyruvate = parseFloat(data.pyruvate);
			        var glycerol = parseFloat(data.glycerol); 
			        var fructose = parseFloat(data.fructose);
			        var succinate = parseFloat(data.succinate); 
			        var glucose = parseFloat(data.glucose);
			        
	   	        var canvas = document.getElementById("canvas");
							var ctx = canvas.getContext("2d");

							var dat = {
									labels: ["acetate", "pyruvate", "glycerol", "fructose", "succinate", "glucose"],
									datasets: [
											{
													label: "",
													fillColor: ["rgba(220,220,220,0.5)", "navy", "red", "orange", "blue", "red", "white"],
													strokeColor: "rgba(220,220,220,1)",
													pointColor: "rgba(220,220,220,1)",
													pointStrokeColor: "#fff",
													pointHighlightFill: "#fff",
													pointHighlightStroke: "rgba(220,220,220,1)",
													data: [acetate, pyruvate, glycerol, fructose, succinate, glucose]
											}
									]
							};


							var myNewChart = new Chart(ctx , {
									type: "bar",
									data: dat, 
							});
			       
			        
				      $("#graphs").show();		
				    });
			});
      
      $( document ).ready(function(){
    $("#list").hide();
    $("#graphs").hide();
     
    
    
    

    
    
    
    
    
    
    
    
});
      
  </script>


  <script type="text/javascript" src="js/canvasjs.min.js"></script>
  <script type="text/javascript" src="js/bootstrap.min.js"></script>
  <script type="text/javascript" src="js/jquery.inview.min.js"></script>
  <script type="text/javascript" src="js/wow.min.js"></script>
  <script type="text/javascript" src="js/mousescroll.js"></script>
  <script type="text/javascript" src="js/smoothscroll.js"></script>
  <script type="text/javascript" src="js/jquery.countTo.js"></script>
  <script type="text/javascript" src="js/lightbox.min.js"></script>
  <script type="text/javascript" src="js/main.js"></script>

</body>
</html>
