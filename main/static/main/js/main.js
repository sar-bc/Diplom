 console.log("main.js");

 window.addEventListener("DOMContentLoaded", function() {
   [].forEach.call( document.querySelectorAll("[type=tel]"), function(input) {
     var keyCode;
     function mask(event) {
       event.keyCode && (keyCode = event.keyCode);
       var pos = this.selectionStart;
       if (pos < 3) event.preventDefault();
       var matrix = "+7 (___) ___ ____",
           i = 0,
           def = matrix.replace(/\D/g, ""),
           val = this.value.replace(/\D/g, ""),
           new_value = matrix.replace(/[_\d]/g, function(a) {
               return i < val.length ? val.charAt(i++) : a
           });
       i = new_value.indexOf("_");
       if (i != -1) {
           i < 5 && (i = 3);
           new_value = new_value.slice(0, i)
       }
       var reg = matrix.substr(0, this.value.length).replace(/_+/g,
           function(a) {
               return "\\d{1," + a.length + "}"
           }).replace(/[+()]/g, "\\$&");
       reg = new RegExp("^" + reg + "$");
       if (!reg.test(this.value) || this.value.length < 5 || keyCode > 47 && keyCode < 58) {
         this.value = new_value;
       }
       if (event.type == "blur" && this.value.length < 5) {
         this.value = "";
       }
     }
 
     input.addEventListener("input", mask, false);
     input.addEventListener("focus", mask, false);
     input.addEventListener("blur", mask, false);
     input.addEventListener("keydown", mask, false);
 
   });
 
 });
//================================
//для отображения пароля
// $('body').on('click', '.password-control', function () {
//   if ($('#edit_password').attr('type') == 'password') {
//       $(this).addClass('view');
//       $('#edit_password').attr('type', 'text');
//   } else {
//       $(this).removeClass('view');
//       $('#edit_password').attr('type', 'password');
//   }
//   return false;
//});
//******** */
//$('body').on('click', '.password-control_new', function () {
//   if ($('#password_new').attr('type') == 'password') {
//       $(this).addClass('view');
//       $('#password_new').attr('type', 'text');
//   } else {
//       $(this).removeClass('view');
//       $('#password_new').attr('type', 'password');
//   }
//   return false;
//});
//******** */
//$('body').on('click', '.password-control_re', function () {
//   if ($('#password_re').attr('type') == 'password') {
//       $(this).addClass('view');
//       $('#password_re').attr('type', 'text');
//   } else {
//       $(this).removeClass('view');
//       $('#password_re').attr('type', 'password');
//   }
//   return false;
//});
//=============================
// const form_edit_password = document.getElementById("form_edit_password");
// if(form_edit_password){
//    let edit_password = document.getElementById("edit_password");
//    let edit_password_error = document.getElementById("edit_password_error");
//    form_edit_password.addEventListener("submit",(e)=>{
//       console.log(edit_password.value)
//    })
// }