document.getElementsByClassName('expand-button').onclick = function() {
  document.getElementsByClassName('special-text').classList.toggle('-expanded');
  
  if (document.getElementsByClassName('special-text').classList.contains('-expanded')) {
    document.getElementsByClassName('expand-button').html('Collapse Content');
  } else {
    document.getElementsByClassName('expand-button').html('Continue Reading');
  }
};

// $('.expand-button').on('click', function(){
//   $('.special-text').toggleClass('-expanded');
  
//   if ($('.special-text').hasClass('-expanded')) {
//     $('.expand-button').html('Collapse Content');
//   } else {
//     $('.expand-button').html('Continue Reading');
//   }
// });

// document.getElementById('start').onclick = function() {
//   var newDiv = document.createElement('div');
//   newDiv.className = '_dash-loading-callback';
//   newDiv.id = 'loading';
//   document.body.appendChild(
//     newDiv,
//     document.getElementById('content'));
// }

// document.getElementById('reset').onclick = function() {
//   document.getElementById('loading').remove();
// }
