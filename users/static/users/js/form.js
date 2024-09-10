
$(document).ready(function () {
console.log("Load form.js")

//==============================
$('#form_phone_edit').submit(function(e){
    e.preventDefault()
    $.ajax({
        type: this.method,
        url: this.action,
        data: $(this).serialize(),
        dataType: 'json',
        success : function(response){
            console.log('ok - ', response)
            if(response.status === 201){
                // window.location.reload()
                $('.response').text(response.response).removeClass('d-none').attr('tabindex', '-1').focus();
                setTimeout(function () {
                    window.location.reload()
                }, 3000);
            }else if (response.status === 400) {
                $('.error_phone').text(response.error).removeClass('d-none').attr('tabindex', '-1').focus();
                setTimeout(function () {
                    $('.error_phone').addClass('d-none')
                }, 3000);
            }
        },
        error: function (response) {
            console.log('err - ', response)
        }

    })

})
//================================
//form_email_edit
$('#form_email_edit').submit(function(e){
    e.preventDefault()
    $.ajax({
        type: this.method,
        url: this.action,
        data: $(this).serialize(),
        dataType: 'json',
        success : function(response){
            console.log('ok - ', response)
            if(response.status === 201){
                $('.response').text(response.response).removeClass('d-none').attr('tabindex', '-1').focus();
                setTimeout(function () {
                    window.location.reload()
                }, 3000);
            }else if (response.status === 400) {
                $('.error_email').text(response.error).removeClass('d-none').attr('tabindex', '-1').focus();
                setTimeout(function () {
                    $('.error_email').addClass('d-none')
                }, 3000);
            }

        },
        error: function (response) {
            console.log('err - ', response)
        }

    })

})
//================================
//form_change_password
$('#form_change_password').submit(function(e){
    e.preventDefault()
    $.ajax({
        type: this.method,
            url: this.action,
            data: $(this).serialize(),
            dataType: 'json',
            success : function(response){
                console.log('ok - ', response)
                if(response.status === 201){
                    // window.location.reload()
                    $('.response').text(response.response).removeClass('d-none').attr('tabindex', '-1').focus();
                setTimeout(function () {
                    window.location.href = '/'
                }, 3000);
                    // window.location.href = '/'
                }else if (response.status === 400) {
                    // $('.alert-danger').text(response.error).removeClass('d-none')
                    let obj = JSON.parse(response.error)
                    // console.log(obj)
                    if(obj.old_password){
                        // console.log(obj.old_password[0]['message'])
                        //error_old
                        $('.error_old').text(obj.old_password[0]['message']).removeClass('d-none').attr('tabindex', '-1').focus();
                    }else{
                        $('.error_old').text("").addClass('d-none')
                    }
                    if(obj.new_password2){
                        // console.log(obj.new_password2[0]['message'])
                        //error_password2
                        $('.error_password2').text(obj.new_password2[0]['message']).removeClass('d-none')
                    }else{
                        $('.error_password2').text("").addClass('d-none')
                    }

                }

            },
            error: function (response) {
                console.log('err - ', response)
            }

    })

})
//================================
$('#show_pass_change').click(function(e){
    // console.log("press")
    if ($('#id_old_password').attr('type') == 'password'){
        $('#id_old_password').attr('type', 'text');
        $('#id_new_password1').attr('type', 'text');
        $('#id_new_password2').attr('type', 'text');
    }else{
        $('#id_old_password').attr('type', 'password');
        $('#id_new_password1').attr('type', 'password');
        $('#id_new_password2').attr('type', 'password');
    }
})
//================================
//form_rec_doc
$('#form_rec_doc').submit(function(e){
    e.preventDefault()
    $.ajax({
        type: this.method,
        url: this.action,
        data: $(this).serialize(),
        dataType: 'json',
        success : function(response){
            console.log('ok - ', response)
            if(response.status === 201){
                // window.location.reload()
                $('.response').text(response.response).removeClass('d-none').attr('tabindex', '-1').focus();
                setTimeout(function () {
                    window.location.reload()
                }, 3000);
            }else if (response.status === 400) {
                $('.error').text(response.error).removeClass('d-none').attr('tabindex', '-1').focus();
                setTimeout(function () {
                    window.location.reload()
                }, 3000);
            }

        },
        error: function (response) {
            console.log('err - ', response)
        }

    })

})
//==============================
//form_send_pokazaniya
$('#form_send_pokazaniya').submit(function(e){
    e.preventDefault()
    $.ajax({
        type: this.method,
        url: this.action,
        data: $(this).serialize(),
        dataType: 'json',
        success : function(response){
            console.log('ok - ', response)
            if(response.status === 201){
                // window.location.reload()
                $('.ok_pokaz').text(response.response).removeClass('d-none').attr('tabindex', '-1').focus();
                setTimeout(function () {
                    window.location.reload()
                }, 3000);
            }else if (response.status === 400) {
                $('.error_pokaz').text(response.error).removeClass('d-none').attr('tabindex', '-1').focus();
                setTimeout(function () {
                    // window.location.reload()
                    $('.error_pokaz').addClass('d-none')
                }, 3000);
            }
            

        },
        error: function (response) {
            console.log('err - ', response)
        }
    })



})
//================================
//form_zayavka_write
$('#form_zayavka_write').submit(function(e){
    e.preventDefault()
    $.ajax({
        type: this.method,
        url: this.action,
        data: $(this).serialize(),
        dataType: 'json',
        success : function(response){
            console.log('ok - ', response)
            if(response.status === 201){
                // window.location.reload()
                $('.ok_zayavka').text(response.response).removeClass('d-none').attr('tabindex', '-1').focus();
                setTimeout(function () {
                    window.location.reload()
                }, 3000);
            }else if (response.status === 400) {
                $('.error_zayavka').text(response.error).removeClass('d-none').attr('tabindex', '-1').focus();
                setTimeout(function () {
                    // window.location.reload()
                    $('.error_zayavka').addClass('d-none')
                }, 3000);
            }
            

        },
        error: function (response) {
            console.log('err - ', response)
        }
    })



})
//================================

})//doc ready