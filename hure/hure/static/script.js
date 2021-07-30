function abreMenu(){
    menu = document.getElementById('menu');
    if(menu.style.width == '0%'){
        menu.style.width = '100%';
        menu.style.marginLeft = '0%';
    }else{
        menu.style.width = '0%';
        menu.style.marginLeft = '-10%';
    }

};

function mudaMenu(){
    menu = document.getElementById('logo');
    banner = document.getElementById('banner-text');
    logo = document.getElementById('logo-text');
    btn = document.getElementById('btn-menu');
    login = document.getElementById('login');
    if(document.body.scrollTop >= 170 && document.body.width < 640){
        menu.classList.add('fixed-top');
        menu.style.height = 'auto';
        banner.style.display = 'none';
        menu.style.textAlign = 'left';
        menu.style.padding = '2%';
        logo.style.marginTop = '1%';
        logo.classList.add('col-4');
        logo.classList.add('float-left');
        btn.classList.add('btn-sm');
        btn.classList.add('float-right');
        btn.classList.remove('btn-lg');
        btn.classList.add('col-6');
        login.style.display = 'none';
    } else if(document.body.scrollTop <= 170 && document.body.width < 640){
        menu.classList.remove('fixed-top');
        menu.style.height = '40%';
        banner.style.display = 'block';
        menu.style.textAlign = 'center';
        menu.style.padding = '4%';
        logo.style.marginTop = '4%';
        btn.classList.add('btn-lg');
        btn.classList.remove('float-right');
        btn.classList.remove('btn-sm');
        logo.classList.remove('col-4');
        btn.classList.remove('col-6');
        logo.classList.remove('float-left');
        login.style.display = 'block'
    }
}