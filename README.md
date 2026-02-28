# DSS 全天 HiPS 批下载脚本

从 DSS2 Color（或任意 HiPS 服务）下载全天 HiPS 图像。  

- 数据源 / Base URL: `http://alasky.u-strasbg.fr/DSS/DSSColor`
- 按 HEALPix 层级遍历 order 0..max_order，逐张下载HiPS 图像；测试时建议使用较小的 max_order，order 越大图像越多，无覆盖区域可能返回 404。
- 默认输出到脚本所在目录（本 dss 文件夹）；可用 `--output DIR` 指定其它目录。

## 用法 / Usage

```bash
python3 dss_hips_download.py [--max-order N] [--output DIR] [--min-order N]
```

## 参数 / Options

| 参数 | 默认 | 说明 |
|------|------|------|
| `--max-order` | 3 | 最大 HEALPix 层级。Order 3=3072 张，4=12288，5=49152。 |
| `--min-order` | 0 | 从该 order 开始下载。 |
| `--output` | 脚本所在目录 | 输出目录。 |

## 示例 / Examples

```bash
python3 dss_hips_download.py --max-order 3
python3 dss_hips_download.py --max-order 5 --output ./my_hips
```

## 说明 / Notes

- HiPS 路径约定：`NorderX/DirYYYY/NpixZZZZ.jpg`（Dir 按 10000 分组）。
- DSS 在无覆盖天区会返回 404。
- 脚本会拉取远端 properties 并合并写入本地的 `properties` / `properties.txt`，其中 `hips_order` 设为本次的 max_order。
