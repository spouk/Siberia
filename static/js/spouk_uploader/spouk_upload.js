/**
 * Created by spouk on 27.03.15.
 */

var FILES = {};

FILES.humanFileSize = function (bytes, si) {
    var thresh = si ? 1000 : 1024;
    if (bytes < thresh) return bytes + ' B';
    var units = si ? ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'] : ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'];
    var u = -1;
    do {
        bytes /= thresh;
        ++u;
    } while (bytes >= thresh);
    return bytes.toFixed(1) + ' ' + units[u];

};
FILES.uploadFiles_addFiletoListFile = function (fileobj) {
//    аргумент ID таблицы для файлов, ищет tbody и добавляет туда файл, fileObj - файловый объект для добавления
    var tbody = document.getElementById('tbody');
    //var table = document.getElementById('');
    //var tbody = table.elements.tbody;

    var tr = document.createElement('tr');
    var progress = '<progress id="progressbar_' + fileobj.name + '" max="100" value="0"></progress>';

    tr.id = "tr" + fileobj.name;
    tbody.appendChild(tr);
    head_names = {
        img: null,
        fname: fileobj.name,
        modified: fileobj.lastModifiedDate,
        type: fileobj.type,
        size: FILES.humanFileSize(fileobj.size, 1024),
        func: null,
        progress: progress,
        refresh: '<i id="refresh_' + fileobj.name + '" class="fa fa-refresh "></i>'
    };

    for (var key in head_names) {
        var td = document.createElement('td');
        td.id = key + fileobj.name;
        td.innerHTML = head_names[key];
        tr.appendChild(td);
        var current_td = document.getElementById(key + fileobj.name);
        if (key == 'img') {
            current_td.innerHTML = "IMG" + fileobj.name;
        }
    }


};

FILES.uploadFiles_createConnector = function () {
    try {
        request = new XMLHttpRequest();
    } catch (trymicrosoft) {
        try {
            request = new ActiveXObject("Msxml2.XMLHTTP");
        } catch (othermicrosoft) {
            try {
                request = new ActiveXObject("Microsoft.XMLHTTP");
            } catch (failed) {
                request = false;
            }
        }
    }
    if (!request) {
        alert("Ошибка инициализации XMLHTTPRequest, обновите или смените браузер, который поддерживает эту возможность");
        console.log("Ошибка инициализации XMLHTTPRequest, обновите или смените браузер, который поддерживает эту возможность");

    }
    return request;
};

FILES.uploadFiles = function () {
    var form = document.forms.ajaxformname;
    //var csrf = document.getElementById('csrf');
    var infopanel = document.getElementById('infopanel');
    var files = form.elements.list_files.files;
    //table
    //csrf.innerHTML = "Количество выбранных файлов: " + files.length;
    if (!files.length) {
        infopanel.innerHTML = "Файлы не выбраны для загрузки на сервер, выберете файлы и попробуйте снова";
    } else {
        infopanel.innerHTML = "";
        for (var i = 0; i < files.length; i++) {
            var file = files[i];

            // создаем объекты для вззаимодействия с файлом и сервером
            var xhrfile = FILES.uploadFiles_createConnector();
            var filedata = new FormData();

            filedata.append(form._csrf_token.name, form._csrf_token.value);
            filedata.append('uploadfile', file);
            xhrfile.open('POST', '/uploader/', true);

            //создаем кнопку прерывания загрузки
            //var placebutton = document.getElementById('func' + file.name);

            //создадим кнопку отмены загрузки
            //var buttonAbort = document.getElementById('abort_button');
            //var buttonAbort = document.createElement('button');
            //buttonAbort.id = "abort"+file.name;
            //document.body.insertBefore(buttonAbort, null);
            //buttonAbort.addEventListener('click', function () {
            //    xhrfile.abort();
            //});
            //csrf.parentNode.insertBefore(buttonAbort, null);
            //получаем псевдоуказатель на текущий индикатор загрузки
            var fname = 'progressbar_' + file.name;
            var indicator = document.getElementById(fname);
            var refresh_element = document.getElementById('refresh_' + file.name);
            var ab = document.getElementById("abort"+file.name);

            //действия при старте загрузки файла ( включаем анимацию иконки загрузки для фана :)
            xhrfile.upload.onloadstart = function () {
                this.progress = indicator;
                this.refresh = refresh_element;
                this.refresh.className += 'fa-spin';
                //this.placeButton = placebutton;
                //this.placeButton.innerHTML = file.name;
                //this.abutton = ab;
                //this.abutton.innerHTML +='Прервать';
                //this.placeButton.appendChild(this.abutton);

            };
            //действия по окончании загрузки файла - меняем иконку на иконку завершения
            xhrfile.upload.onloadend = function () {
                this.refresh.className = 'fa fa-check-square-o';

            };
            //тут действия производимые во время периода загрузки файла на сервер - тут отображем прогресс
            xhrfile.upload.onprogress = function (e) {
                infopanel.innerHTML = "Загружаемый файл " + file.name + "   [" + e.loaded + "]" + "[" + (e.total / 1024) * 100 + "]" + (e.loaded / e.total) * 100;
                this.progress.value = (e.loaded / e.total) * 100;
            };
            //главная функция обработчик ответа с сервера
            xhrfile.onreadystatechange = function () {
                infopanel.innerHTML = "Файл " + file.name + " Ответ с сервера: " + xhrfile.responseText;
                //refresh.className = 'fa fa-check-square-o';
            };

            //прерывание загрузки файлов
            //var buttonAbort = document.getElementById('abort_button');
            //if (!buttonAbort) {
            //    var placebutton = document.getElementById('func' + file.name);
            //    var buttonAbort = document.createElement('button');
            //    buttonAbort.id = "abort_button";
            //    placebutton.appendChild(buttonAbort);
            //}

            //отправка файла
            xhrfile.send(filedata);
        }
    }
    //infopanel.innerHTML = "Можно загружать";
    //return;
};
FILES.uploadFiles_onchange = function () {
    var form = document.forms.ajaxformname;
    var files = form.elements.list_files.files;
    //очистка предыдущих файлов если были
    document.getElementById('tbody').innerHTML = "";
    //активация кнопки отправки файлов на сервер при наличии файлов для отправки вообще в форме
    if (files.length) {
        document.getElementById('sendbutton').disabled = false;
    } else {
        document.getElementById('sendbutton').disabled = true;
    }
    //создать список объект с файлами где ключ имя файла и значение - сам файловый объект
    var obj_files = {};
    for (var i = 0, len = files.length; i < len; i++) {
        var file = files[i];
        obj_files[file.name] = "Not checked";
    }
    //добавление новых - выбранных файлов
    for (var i = 0, len = files.length; i < len; i++) {
        var file = files[i];
        FILES.uploadFiles_addFiletoListFile(file);
        console.log('File ' + file.name);
        //
        ////проверить наличия такого файла на удаленном сервере путем отправки "скрытого" ajax запроса по имени
        //var xhr = FILES.getConnector();
        //xhr.open('GET', '/checkfile/' + file.name, true);
        //xhr.onreadystatechange = function () {
        //    //    получаем ответ с сервера
        //    if (xhr.readyState == 4) {
        //        var answer = JSON.parse(xhr.responseText);
        //        obj_files[file.name] = answer[file.name];
        //        console.log("ObjectFile==> " + obj_files[file.name]);
        //        for (var key in answer) {
        //            console.log(key + "  " + answer[key]);
        //        }
        //    }
        //};
        //xhr.send(null);

    }

};

