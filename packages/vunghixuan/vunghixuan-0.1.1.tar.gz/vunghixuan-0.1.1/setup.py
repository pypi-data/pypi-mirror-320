# setup.py

from setuptools import setup, find_packages

# setup(
#     name='vunghixuan_package',
#     version='0.1.0',
#     description='API, OTP, Create Project',
#     author='Đăng Thanh Vũ',
#     author_email='vunghixuan@gmail.com',
#     packages=find_packages(where='src'), #Tìm kiếm và liệt kê các gói con trong thư mục src, nơi chứa mã nguồn chính.
#     package_dir={'': 'src'}, #Chỉ định thư mục chứa các gói, ở đây là {'': 'src'} nghĩa là gói nằm trong thư mục src.
#     install_requires=['python-dotenv','requests', 'pyotp', 'setuptools'],  # Các gói phụ thuộc
#     entry_points={
#         'console_scripts': [
#             'vunghixuan_package=vunghixuan_package.main:main'
#         ]
#     }
# )


from setuptools import setup, find_packages

setup(
    name='vunghixuan',
    version='0.1.1',
    packages=find_packages(where='src'),
    description='Get API, OTP, Create Project, Date_created = 2025-01-08',
    author='Đặng Thanh Vũ',
    author_email='vunghixuan@gmail.com',
    package_dir={'': 'src'},
    install_requires=[
        'pyotp',
    ],
    entry_points={
        'console_scripts': [
            'vunghixuan = vunghixuan.main:main',
        ],
    },
)

"""
Quy trình phát hành gói Python bao gồm nhiều bước quan trọng, mỗi bước đều có chức năng riêng biệt:

1. pip install .: Lệnh này được sử dụng để cài đặt gói Python từ thư mục hiện tại. Nó sẽ tìm kiếm file setup.py và cài đặt gói theo cấu hình đã định nghĩa.

2. python setup.py sdist bdist_wheel: Lệnh này tạo ra các gói phân phối. sdist tạo ra gói nguồn, trong khi bdist_wheel tạo ra gói nhị phân (wheel). Điều này giúp người dùng có thể cài đặt gói một cách dễ dàng hơn.

Vào folder dist lấy thông tin file và: Sau khi tạo gói, bạn cần vào thư mục dist để tìm file gói đã tạo.

3. pip install dist/vunghixuan-0.1.0-py3-none-any.whl: Lệnh này cài đặt gói đã được tạo ra từ thư mục dist.

4. Cập nhật nếu hỏi: pip install dist/vunghixuan-0.1-py3-none-any.whl --force-reinstall: Nếu bạn cần cập nhật gói đã cài đặt, lệnh này sẽ cài đặt lại gói, bất kể phiên bản hiện tại.



5. twine upload dist/* -u __token__ -p pypi-AgEIcHlwaS5vcmcCJDJkY2EzOTEyLTZjNzMtNDdhMy05YjBmLWM1MWY4NGZjNTZmOQACKlszLCI4OWIwMTU4NS0wNzFhLTQ1M2ItYTU2Yi1lMjU2YTAyYzUzMzkiXQAABiBFb0kaUKmOKW4r199X2i1zZMfbcNKi1DKnnR31hYkpMg
Tóm lại, bước 1 và 2 tạo môi trường local, trong khi bước 5 là bước tải lên gói lên PyPI.

6. Sử dụng lệnh gỡ bỏ: twine remove <tên-gói> --version <phiên-bản> -u __token__ -p pypi

"""

# Bỏ mã sau: pypi-AgEIcHlwaS5vcmcCJGRmOTZjMWEwLTg3YjEtNDQ4My1iMzc3LTVmZmIxMzdiYzkxMgACKlszLCI4OWIwMTU4NS0wNzFhLTQ1M2ItYTU2Yi1lMjU2YTAyYzUzMzkiXQAABiCqSM0HmXMCrq31YYQOx_5Up0gQaH0xbg21VpYen9CKlw
"""
[pypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmcCJGRmOTZjMWEwLTg3YjEtNDQ4My1iMzc3LTVmZmIxMzdiYzkxMgACKlszLCI4OWIwMTU4NS0wNzFhLTQ1M2ItYTU2Yi1lMjU2YTAyYzUzMzkiXQAABiCqSM0HmXMCrq31YYQOx_5Up0gQaH0xbg21VpYen9CKlw


  lần 2: pypi-AgEIcHlwaS5vcmcCJDJkY2EzOTEyLTZjNzMtNDdhMy05YjBmLWM1MWY4NGZjNTZmOQACKlszLCI4OWIwMTU4NS0wNzFhLTQ1M2ItYTU2Yi1lMjU2YTAyYzUzMzkiXQAABiBFb0kaUKmOKW4r199X2i1zZMfbcNKi1DKnnR31hYkpMg

  [pypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmcCJDJkY2EzOTEyLTZjNzMtNDdhMy05YjBmLWM1MWY4NGZjNTZmOQACKlszLCI4OWIwMTU4NS0wNzFhLTQ1M2ItYTU2Yi1lMjU2YTAyYzUzMzkiXQAABiBFb0kaUKmOKW4r199X2i1zZMfbcNKi1DKnnR31hYkpMg

Mã Otp:
    obj = Otp('OXATAFVTTUIVMXNQCKMZAOFZYUYE6MGZ').get_otp()

    src/
        │
        ├── vunghixuan/
        │   ├── __init__.py
        │   ├── create_project.py
        │   ├── api_and_otp.py
        │   └── main.py
        │
        └── setup.py

"""
