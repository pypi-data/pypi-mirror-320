## 简介

使用cythonize将python代码一键加密为so或pyd。支持单个文件加密，整个项目加密。
(seal your pyfiles or project by using cythonize.)

Git仓库地址: https://github.com/limoncc/sealpy.git

## 安装

    pip install sealpy3

## 使用方法

    sealpy -i "xxx project dir" [-o output dir]

加密后的文件默认存储在 dist/project_name/ 下