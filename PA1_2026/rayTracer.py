#!/usr/bin/env python3
# -*- coding: utf-8 -*
# sample_python aims to allow seamless integration with lua.
# see examples below

import os
import sys
import pdb  # use pdb.set_trace() for debugging
import code  # or use code.interact(local=dict(globals(), **locals()))  for debugging.
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
       return v
    return v / norm

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = normalize(direction)


class Color:
    def __init__(self, R, G, B):
        self.color = np.array([R, G, B]).astype(np.float64)

    # Gamma corrects this color.
    # @param gamma the gamma value to use (2.2 is generally used).
    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma;
        self.color = np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0, 1) * 255).astype(np.uint8)


class Shader:
    def __init__(self, name, shader_type, diffuseColor, specularColor=None, exponent=None):
        self.name = name
        self.type = shader_type
        self.diffuseColor = diffuseColor

        self.specularColor = specularColor if specularColor is not None else np.array([0.0, 0.0, 0.0])
        self.exponent = exponent if exponent is not None else 0.0


class Sphere:
    def __init__(self, center, radius, shader_ref):
        self.center = center
        self.radius = radius
        self.shader_ref = shader_ref

    # 광선과 구의 충돌 여부와 거리 계산
    def intersect(self, ray):
        oc = ray.origin - self.center

        a = np.dot(ray.direction, ray.direction)
        b = 2.0 * np.dot(ray.direction, oc)
        c = np.dot(oc, oc) - self.radius * self.radius

        discriminant = b * b - 4 * a * c

        if discriminant < 0:
            return -1.0

        sqrt_d = np.sqrt(discriminant)
        t1 = (-b - sqrt_d) / (2.0 * a)
        t2 = (-b + sqrt_d) / (2.0 * a)

        if t1 > 0:
            return t1
        if t2 > 0:
            return t2

        return -1.0

class Light:
    def __init__(self, position, color):
        self.position = position
        self.color = color


def main():
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    # set default values
    viewDir = np.array([0, 0, -1]).astype(np.float64)
    viewUp = np.array([0, 1, 0]).astype(np.float64)
    viewProjNormal = -1 * viewDir  # you can safely assume this. (no examples will use shifted perspective camera)
    viewWidth = 1.0
    viewHeight = 1.0
    projDistance = 1.0
    intensity = np.array([1, 1, 1]).astype(np.float64)  # how bright the light is.
    print(np.cross(viewDir, viewUp))

    imgSize = np.array(root.findtext('image').split()).astype(np.int32)

    for c in root.findall('camera'):
        viewPoint = np.array(c.findtext('viewPoint').split()).astype(np.float64)
        viewDir = np.array(c.findtext('viewDir').split()).astype(np.float64)
        viewUp = np.array(c.findtext('viewUp').split()).astype(np.float64)

        viewWidth_text = c.findtext('viewWidth')
        viewWidth = float(viewWidth_text) if viewWidth_text is not None else 1.0

        viewHeight_text = c.findtext('viewHeight')
        viewHeight = float(viewHeight_text) if viewHeight_text is not None else 1.0

        projDistance_text = c.findtext('projDistance')
        projDistance = float(projDistance_text) if projDistance_text is not None else 1.0

    shaders = {}
    for c in root.findall('shader'):
        diffuseColor_c = np.array(c.findtext('diffuseColor').split()).astype(np.float64)
        name = c.get('name')
        shader_type = c.get('type')
        print('name', c.get('name'))
        print('diffuseColor', diffuseColor_c)

        specularColor = None;
        exponent = None;
        if shader_type == 'Phong':
            specularColor = np.array(c.findtext('specularColor').split()).astype(np.float64)
            exponent = float(c.findtext('exponent'))

        shaders[name] = Shader(name, shader_type, diffuseColor_c, specularColor, exponent)

    spheres = []
    for surface in root.findall('surface'):
        if surface.get('type') == 'Sphere':
            center = np.array(surface.findtext('center').split()).astype(np.float64)
            radius = float(surface.findtext('radius'))

            shader_node = surface.find('shader')
            shader_ref = shader_node.get('ref') if shader_node is not None else ""

            spheres.append(Sphere(center, radius, shader_ref))

    lights = []
    for light in root.findall('light'):
        position = np.array(light.findtext('position').split()).astype(np.float64)

        c_text = light.findtext('color')
        i_text = light.findtext('intensity')

        if c_text is not None:
            color = np.array(c_text.split()).astype(np.float64)
        elif i_text is not None:
            color = np.array(i_text.split()).astype(np.float64)
        else:
            color = np.array([1.0, 1.0, 1.0])

        lights.append(Light(position, color))

    # Create an empty image
    channels = 3
    img = np.zeros((imgSize[1], imgSize[0], channels), dtype=np.uint8)
    img[:, :] = 0


    w_dir = normalize(viewDir)

    u_dir = normalize(np.cross(viewDir, viewUp))

    v_dir = normalize(np.cross(u_dir, w_dir))

    image_center = viewPoint + w_dir * projDistance

    pixel_width = viewWidth / imgSize[0]
    pixel_height = viewHeight / imgSize[1]

    # 픽셀로 ray 쏘기
    for y in np.arange(imgSize[1]):
        for x in np.arange(imgSize[0]):
            u_offset = (x + 0.5 - imgSize[0] / 2.0) * pixel_width
            v_offset = (imgSize[1] / 2.0 - y - 0.5) * pixel_height

            pixel_point = image_center + (u_offset * u_dir) + (v_offset * v_dir)

            ray_dir = pixel_point - viewPoint
            ray = Ray(viewPoint, ray_dir)

            # Sphere 충돌 검사
            hit_t = float('inf')
            hit_sphere = None

            for sphere in spheres:
                t = sphere.intersect(ray)
                if t > 0 and t < hit_t:
                    hit_t = t
                    hit_sphere = sphere

            # 픽셀 색상, 셰이딩
            if hit_sphere is not None:
                hit_point = ray.origin + hit_t * ray.direction

                normal = normalize(hit_point - hit_sphere.center)

                shader = shaders.get(hit_sphere.shader_ref)
                diffuse_color = shader.diffuseColor if shader is not None else np.array([1.0, 1.0, 1.0])

                final_color = np.array([0.0, 0.0, 0.0])

                view_dir = normalize(viewPoint - hit_point)

                for light in lights:
                    light_vec = light.position - hit_point
                    light_dist = np.linalg.norm(light_vec)
                    light_dir = light_vec / light_dist if light_dist > 0 else np.array([0, 0, 0])

                    # 그림자
                    shadow_origin = hit_point + normal * 1e-4
                    shadow_ray = Ray(shadow_origin, light_dir)

                    is_in_shadow = False
                    for sphere in spheres:
                        t = sphere.intersect(shadow_ray)
                        if t > 0 and t < light_dist:
                            is_in_shadow = True
                            break

                    if is_in_shadow:
                        continue

                    # 난반사
                    n_dot_l = np.dot(normal, light_dir)
                    diffuse_factor = max(0.0, n_dot_l)
                    color_contribution = diffuse_color * light.color * diffuse_factor

                    # 정반사
                    if shader is not None and shader.type == 'Phong' and diffuse_factor > 0:
                        half_vector = normalize(light_dir + view_dir)
                        n_dot_h = max(0.0, np.dot(normal, half_vector))
                        specular_factor = np.power(n_dot_h, shader.exponent)

                        specular_contribution = shader.specularColor * light.color * specular_factor
                        color_contribution += specular_contribution

                    final_color += color_contribution

            else:
                final_color = np.array([0.0, 0.0, 0.0])

            color_obj = Color(final_color[0], final_color[1], final_color[2])

            color_obj.gammaCorrect(2.2)

            img[y][x] = color_obj.toUINT8()

    rawimg = Image.fromarray(img, 'RGB')
    # rawimg.save('out.png')
    rawimg.save(sys.argv[1] + '.png')


if __name__ == "__main__":
    main()
