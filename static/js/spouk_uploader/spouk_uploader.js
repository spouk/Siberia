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

/**
 * Формирует таблицу со списком файлов выбранных для загрузки на сервер
 */
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
        func: '<span id="func_' + fileobj.name + '"></span>',
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

/**
 *  СОздает коннектор для подклюения к серверу
 */
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
//
//FILES.uploadFiles = function () {
//    var form = document.forms.ajaxformname;
//    //var csrf = document.getElementById('csrf');
//    var infopanel = document.getElementById('infopanel');
//    var files = form.elements.list_files.files;
//    //table
//    //csrf.innerHTML = "Количество выбранных файлов: " + files.length;
//    if (!files.length) {
//        infopanel.innerHTML = "Файлы не выбраны для загрузки на сервер, выберете файлы и попробуйте снова";
//    } else {
//        infopanel.innerHTML = "";
//        for (var i = 0; i < files.length; i++) {
//            var file = files[i];
//            console.log('FILENAME ===>', file.name);
//            // создаем объекты для вззаимодействия с файлом и сервером
//            var xhrfile = FILES.uploadFiles_createConnector();
//            var filedata = new FormData();
//
//            filedata.append(form._csrf_token.name, form._csrf_token.value);
//            filedata.append('uploadfile', file);
//            xhrfile.open('POST', '/uploader/', true);
//
//            //создаем кнопку прерывания загрузки
//            //var placebutton = document.getElementById('func' + file.name);
//
//            //создадим кнопку отмены загрузки
//            //var buttonAbort = document.getElementById('abort_button');
//            //var buttonAbort = document.createElement('button');
//            //buttonAbort.id = "abort"+file.name;
//            //document.body.insertBefore(buttonAbort, null);
//            //buttonAbort.addEventListener('click', function () {
//            //    xhrfile.abort();
//            //});
//            //csrf.parentNode.insertBefore(buttonAbort, null);
//            //получаем псевдоуказатель на текущий индикатор загрузки
//            var fname = 'progressbar_' + file.name;
//            var indicator = document.getElementById(fname);
//            var refresh_element = document.getElementById('refresh_' + file.name);
//            var ab = document.getElementById("abort" + file.name);
//
//            //действия при старте загрузки файла ( включаем анимацию иконки загрузки для фана :)
//            xhrfile.upload.onloadstart = function () {
//                this.progress = indicator;
//                this.refresh = refresh_element;
//                this.refresh.className += 'fa-spin';
//                //this.placeButton = placebutton;
//                //this.placeButton.innerHTML = file.name;
//                //this.abutton = ab;
//                //this.abutton.innerHTML +='Прервать';
//                //this.placeButton.appendChild(this.abutton);
//
//            };
//            //действия по окончании загрузки файла - меняем иконку на иконку завершения
//            xhrfile.upload.onloadend = function () {
//                this.refresh.className = 'fa fa-check-square-o';
//
//            };
//            //тут действия производимые во время периода загрузки файла на сервер - тут отображем прогресс
//            xhrfile.upload.onprogress = function (e) {
//                //infopanel.innerHTML = "Загружаемый файл " + file.name + "   [" + e.loaded + "]" + "[" + (e.total / 1024) * 100 + "]" + (e.loaded / e.total) * 100;
//                //infopanel.innerHTML = "Загружаемый файл " + file.name + "   [" +  FILES.humanFileSize(e.loaded, 'kB')+ "]" + "[" +  FILES.humanFileSize((e.loaded/1024) * 100, 'kB') + "]" +  FILES.humanFileSize((e.loaded / e.total) * 100, 'kB');
//                infopanel.innerHTML = "Загружаемый файл <strong> " + file.name + "</strong>  загружено  [" + FILES.humanFileSize(e.loaded, 'kB') + "]    из   " + FILES.humanFileSize(e.total, 'kB');
//
//                console.log('HUMAN SIZE: ', FILES.humanFileSize(e.loaded, 'kB'));
//                this.progress.value = (e.loaded / e.total) * 100;
//            };
//            //главная функция обработчик ответа с сервера
//            xhrfile.onreadystatechange = function () {
//                var answer;
//                if (xhrfile.readyState == 4 && xhrfile.status == 200) {
//                    //var answer_from_server = JSON.parse(xhrfile.responseText);
//                    answer = xhrfile.responseText;
//                    console.log(answer_from_server);
//                    infopanel.innerHTML = infopanel.innerText + "Файл " + file.name + " Ответ с сервера: " + answer_from_server;
//                    //refresh.className = 'fa fa-check-square-o';
//                }
//            };
//
//            //прерывание загрузки файлов
//            //var buttonAbort = document.getElementById('abort_button');
//            //if (!buttonAbort) {
//            //    var placebutton = document.getElementById('func' + file.name);
//            //    var buttonAbort = document.createElement('button');
//            //    buttonAbort.id = "abort_button";
//            //    placebutton.appendChild(buttonAbort);
//            //}
//
//            //отправка файла
//            xhrfile.send(filedata);
//        }
//    }
////infopanel.innerHTML = "Можно загружать";
////return;
//};

/**
 *  Делает активными кнопку загрузки при выборе файлов, формирует список файлов для передачи функции загрузчика
 */
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
    console.log('OBJ_FILES', obj_files);
    //добавление новых - выбранных файлов
    for (var i = 0, len = files.length; i < len; i++) {
        var file = files[i];
        var ftype = file.type;
        if (ftype.indexOf('image')+1) {
            FILES.uploadFiles_addFiletoListFile(file);
            console.log('File ' + file.name);
        } else {
            console.log('File BAD FORMAT NOT IMAGE --> ' + file.name);
        }
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
/**
 *  функция загрузчик одного файла с обработкой результата
 *  параметры file - файловый объект для передачи,
 *            method - post/get,
 *            url - обработчик,
 *            form - текущая форма(document.getElementbyID()
 */
FILES.upfile = function (parameters) {
    //передача JSON структуры с параметрами вызова
    //файловый объект
    var file = parameters.file;
    //метода отправки GET/POST
    var method = parameters.method;
    //URL обработчика передачи
    var url = parameters.url;
    //csrf token
    var form = parameters.form;
    //product id
    var product_id = parameters.product_id;

    if (file) {
        console.log(file.name);
        //получаю объект дерева куда буду передавать данные о состоянии процесса передачи файла
        var infopanelobj = 'func_' + file.name;
        var infopanel = document.getElementById(infopanelobj);
        //создаю хэндлер для обработки аяксовой сессии
        var xhrfile = FILES.uploadFiles_createConnector();
        //файловый контейнер для передачи данных
        var filedata = new FormData();
        //получаю прогрессбар для отображения прогресса загрузки
        var fname = 'progressbar_' + file.name;
        var indicator = document.getElementById(fname);

        //получаю элемент кнопки  которую буду обновлять по результату загрузки
        var refresh_element = document.getElementById('refresh_' + file.name);
        //var ab = document.getElementById("abort" + file.name);
        //добавляю токен на отправляюмую форму,т.к. метод отправки запроса -  POST
        filedata.append(form._csrf_token.name, form._csrf_token.value);
        //добавляю файловый хэндлер
        filedata.append('uploadfile', file);
        //открваю http соединение по методу post с урлом и включением асинхронной обработки результата и передачи данных
        xhrfile.open(method, url+product_id, true);

        //действия при старте загрузки файла ( включаем анимацию иконки загрузки для фана :)
        xhrfile.upload.onloadstart = function () {
            //делаем привязку ранее полученных элементов дерева к текущему процессу аякса
            this.progress = indicator;
            this.refresh = refresh_element;
            this.refresh.className += 'fa-spin';
            this.infopanel = infopanel;

            //this.placeButton = placebutton;
            //this.placeButton.innerHTML = file.name;
            //this.abutton = ab;
            //this.abutton.innerHTML +='Прервать';
            //this.placeButton.appendChild(this.abutton);

        };
        //действия по окончании загрузки файла - меняем иконку на иконку завершения
        xhrfile.upload.onloadend = function () {
            //if (answer == true)
            //    this.refresh.className = 'fa fa-check-square-o';
            //    this.td.className="success";
            //if (answer == false)
            //    this.refresh.className = 'fa fa-ban';
            //    this.td.className="danger";
        };
        //тут действия производимые во время периода загрузки файла на сервер - тут отображем прогресс
        xhrfile.upload.onprogress = function (e) {
            //infopanel.innerHTML = "Загружаемый файл " + file.name + "   [" + e.loaded + "]" + "[" + (e.total / 1024) * 100 + "]" + (e.loaded / e.total) * 100;
            //infopanel.innerHTML = "Загружаемый файл " + file.name + "   [" +  FILES.humanFileSize(e.loaded, 'kB')+ "]" + "[" +  FILES.humanFileSize((e.loaded/1024) * 100, 'kB') + "]" +  FILES.humanFileSize((e.loaded / e.total) * 100, 'kB');
            //infopanel.innerHTML = "Загружаемый файл <strong> " + file.name + "</strong>  загружено  [" + FILES.humanFileSize(e.loaded, 'kB') + "]    из   " + FILES.humanFileSize(e.total, 'kB');
            this.infopanel.innerHTML = FILES.humanFileSize(e.loaded, 'kB');
            //console.log('HUMAN SIZE: ', FILES.humanFileSize(e.loaded, 'kB'));
            this.progress.value = (e.loaded / e.total) * 100;
        };
        //главная функция обработчик ответа с сервера
        xhrfile.onreadystatechange = function () {
            if (xhrfile.readyState == 4 && xhrfile.status == 200) {
                var answer_from_server = JSON.parse(xhrfile.responseText);
                var elem = 'refresh_' + file.name;
                var refresh_this_file = document.getElementById(elem);
                //получаю текущую td колонку
                var tr = 'tr' + file.name;
                var trfile= document.getElementById(tr);
                if (answer_from_server.status == true) {
                    refresh_this_file.className = 'fa fa-check-square-o';
                    trfile.className="success";
                } else {
                    refresh_this_file.className = 'fa fa-ban';
                    trfile.className="danger";
                }
                //infopanel.innerHTML = infopanel.innerText + "Файл " + file.name + " Ответ с сервера: " + answer_from_server.status;

            }
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
};


FILES.upload_async_files = function (product_id) {
    //product_id идентификатор продукта
    var product_id = product_id;
    //поулчаю форму
    var form = document.forms.ajaxformname;
    //получаю панель для вывода информации о операциях
    var infopanel = document.getElementById('infopanel');
    //получаю список файловых объектов
    form.elements.list_files = undefined;
    var files = form.elements.list_files.files;
    if (!files.length) {
        infopanel.innerHTML = "Файлы не выбраны для загрузки на сервер, выберете файлы и попробуйте снова";
    } else {
        infopanel.innerHTML = "";
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            console.log('FILENAME ===>', file.name);
            param = {
                method: "POST",
                url: "/uploader/",
                product_id: product_id,
                file: file,
                form: form

            };
            FILES.upfile(param);
        }
    }

};