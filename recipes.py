# import ...
# from ... import ...
# recipe/rule
# single_page, many_pages, ... [подобрать названия поудачнее]

# Кроме имён метрик должны быть изестны их типы.
# Какое-то описание общее, необходимое для представления, хранения и пр.

recipes = dict()
sources = dict()
destinations = dict()
# targets = dict()
storages = dict()

recipes['stand'] = {
    "names": [
        "id",
        "stand_name",
    ],
    "links": None,
    "storage": {
        "name": "sqlite_alchemy_local",
    },
    "destination": {
        "name": "sqlite_alchemy_local",
    },
    "source": {
        "name": "sqlite_alchemy_local",
    },
}

recipes['page'] = {
    "names": [
        "id",       # тип?
        "url",      # тип?
        "label",    # тип?
        "stand_id", # тип?
    ],
    "links": {
        "stand_id": {
            "stand": "id", # [..., ..., ...]; {}; ...
            ""
        }
    },
    "storage": {
        "name": "sqlite_alchemy_local",
    },
    "destination": {
        "name": "sqlite_alchemy_local",
    },
    "source": {
        "name": "sqlite_alchemy_local",
    },
}

# recipes['har_data'] = {
recipes['measurement'] = {
    "names": [
        "id",
        "dtime",
        "url_id",
        "content_time",
        "total_files",
        "html_files",
        "css_files",
        "js_files",
        "img_files",
        "xhr_files",
        "font_files",
        "page_size",
        "html_size",
        "css_size",
        "js_size",
        "img_size",
        "xhr_size",
        "font_size",
        "traffic_size",
        "har_link",
        "screens_link",
        "browser_cache_is_used",
        "version",
        "build",
        "core_version",
        "core_build",
        "ws_version",
        "ws_build",
        "controls_version",
        "controls_build",
        "status",
    ]
    "storage": {
        "name": "sqlite_alchemy_local",
    },
    "destination": {
        "name": "sqlite_alchemy_local",
    },
    "source": {
        "name": "sqlite_alchemy_local",
    },
}

storages['sqlite_alchemy'] = {
    "sqlite_alchemy_local": {
        "type": "sqlalchemy", # storage_class?
        "specific": {
            "file_name": "database/perfang.db",
        }
    }
        "storage_class": "...", # from import?

}

storages['har_files_slave'] = {
    
}
