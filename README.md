# AT91FirmwareMaker
一个适用于 ATMEL AT91 系列 SOC 的固件制作工具，将 bootstrap、uboot、 kernel、 rootfs 等二进制文件合并成一个统一的文件，方便使用 SAM-BA 烧写

## 文件说明

	|
	|--- fwmaker.py				# Firmware Maker 包
	|--- FirmwareMaker.py		# Firmware Maker 命令行工具
	|--- FirmwareMakerGui.py	# Firmware Maker Qt 图形界面工具
	

## 打包说明
	
打包命令行工具：

	pyinstaller -F -i icon.ico FirmwareMaker.py
	
打包图形界面工具

	pyinstaller -F -w -i icon.ico FirmwareMakerGui.py
		
	

## 使用说明

软件提供了命令行工具（FirmwareMaker）和的图形化操作工具（FirmwareMakerGui）根据需要使用。图形化工具提供：加载、另存为配置文件的操作，可以根据二进制文件大小，自动调节预置空间大小，可以根据需要预置不同的配置文件，用来生成不同的固件，一下将着重介绍命令行工具。

### 1、操作流程

在使用软件生成固件之前，首先要创建一个 `.json` 的配置文件（可以通过软件生成默认的配置）。这个配置文件描述了：如何生成固件，各个二进制文件在硬盘中的存放位置，以及在固件中的偏移，预留大小等信息。软件根据这个配置文件，最终生成固件，最终生成的固件保存在 `firmware` 目录中。以下是操作流程：

1. 带选项 `-c` 或 `-d` 的方式启动软件，让软件生成默认的配置文件 `setting.json`

2. 打开 `setting.json` 根据使用的实际情况，修改 `setting.josn` 中的参数配置选项

3. 再次执行软件，最终生成固件。

### 2、软件选项

	-h	--help		显示帮助信息

	-v	--verbose	让软件输出相信的操作步骤

	-e	--essential	生成包含:'bootstrap', 'kernel', 'rootfs' 等固件必须文件的的默认配置
	
	-d	--default	生成包含：'bootstrap', 'u-boot', 'u-boot env', 'dtb', 'kernel', 'rootfs' 等文件的默认配置

	-o	--output=	指定输出固件的名称，不指定，将使用默认固件的名称为 `firmware.bin`

	-c	--conf=		指定配置文件名称，软件将根据指定配置文件的设置生成固件，不指定，软件将会在当前目录中寻找默认配置 `setting.json`

### 3、配置文件说明

一下是一个用于 ATMEL AT91SAM9G20 SOC 固件配置文件的例子：

	[
    	{
        	"bootstrap": {
        	    "path": "at91sam9g20ek-nandflashboot-3.1.bin",
        	    "size": "16K",
        	    "offset": "0x0"
        	}
    	},
    	{
        	"kernel": {
        	    "path": "Image",
        	    "size": "3M",
        	    "offset": "1M"
        	}
    	},
    	{
        	"rootfs": {
        	    "path": "rootfs_cramfs.bin",
        	    "size": "4M",
        	    "offset": "4M"
        	}
    	}
	]


上面的配置文件中说明：

- 生成固件需要三个文件模块，分别是：bootstrap, kernel, rootfs。

- bootstrap 在硬盘中的存放位置是当前目录中的 "at91sam9g20ek-nandflashboot-3.1.bin"文件, 为 bootstarp 预留的空间为 16K，它在固件中的偏移为 0（AT91 Bootstrap， 必须在 0 偏移）。

- kernel 在硬盘中的存放位置是当前目录中的 "Image" 文件，为 kernel 预留的空间为 3M, 它在固件中的偏移为 1M。

- rootfs 硬盘中的存放位置是当前目录中的 "rootfs_cramfs.bin" 文件，为 rootfs 预留的空间为 4M，它在固件中的偏移为 4M。


整个 Firmware 的映射图为：

	0 	- 1M	:	bootstrap (最大 16K)
	1M  - 4M	:	kernel	  (最大 3M)
	4M	- 8M	:	rootfs	  (最大 4M)


 





 
