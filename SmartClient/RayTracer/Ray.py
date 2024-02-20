import Color
import numpy
import Point

# A class that represents a ray with an origin and direction. 
# Additionaly takes argument "dict" which is a dictionary of all the scene information
class Ray: 
    # Init
    def __init__(self, dict, spheres, lights):
        self.background = Color.Color([0.0, 0.0, 0.0])
        self.ray = Point.Point([0.0,0.0,0.0])
        self.eye = Point.Point([0.0,0.0,0.0])
        self.dict = dict
        self.spheres = spheres
        self.lights = lights
    
    # Multiply
    def __mul__(self, other):
        return [self.ray[0] * other, self.ray[1] * other, self.ray[2] * other]

    # Updates the self.ray value to have the right pixel cooridnates
    def update_eye_ray(self, u, v, width, height):
        # Find pixel 
        new_u = float(self.dict.get("LEFT")[0]) + float(self.dict.get("RIGHT")[0]) * 2 * u / width
        new_v = -(float(self.dict.get("BOTTOM")[0]) + float(self.dict.get("TOP")[0]) * 2 * v / height)
        self.ray = Point.Point([float(new_u), float(new_v), -float(self.dict.get("NEAR")[0])]) 
        self.background = Color.Color(self.dict.get("BACK"))
    
    # Function to call the trace in the main method
    def raytrace(self):
        col, count = self._trace(self, 0) 
        return col

    # Function that runs the raytracing recursion loop
    def _trace(self, ray, bounces):
        # Color set initialy to black
        color = Color.Color([0.0, 0.0, 0.0])

        # If at max depth then return black
        if bounces > 2:
            return color, bounces

        # Find closest sphere
        closest_point_distance, sphere = self._closest_intersection(ray.ray, ray.eye)

        # If there is no sphere return background
        if closest_point_distance == numpy.inf and bounces == 0:
            return self.background, bounces
        
        # If this is a bounce ray that doesn't hit anything, return black
        elif closest_point_distance == numpy.inf:
            return Color.Color([0.0, 0.0, 0.0]), bounces

        # Find point on sphere
        point_on_sphere = ray.eye + ray.ray*closest_point_distance

        # Check if each light hits or misses the point and give it the appropriate colour
        for light in self.lights:
            ambient_effect = Color.Color(self.dict.get("AMBIENT"))

            # Get shadow ray colors
            diffuse, specular = self._calculate_shadow_ray(light, sphere, point_on_sphere)

            # Add colours together
            color += diffuse
            color += specular

        # Values to calculate reflection and ambient
        ka = float(sphere.attributes[0]) 
        kr = float(sphere.attributes[3])

        # Get reflected ray
        reflection_ray = self._calculate_reflection_ray(ray, sphere, point_on_sphere)

        # Add reflected color if any
        ref_col, bounces = self._trace(reflection_ray, bounces+1)
        color += Color.Color([ref_col.r*kr, ref_col.g*kr, ref_col.b*kr])

        # Get final Color
        ambient = Color.Color([ka*ambient_effect.r*sphere.col.r, ka*ambient_effect.g*sphere.col.g, ka*ambient_effect.b*sphere.col.b])
        color += ambient # Ambient 
        return color, bounces

    # Function that returns the closest sphere and the distance of the point that lies on it
    def _closest_intersection(self, dir, start):
        # Intitialy assume there is no intersection
        close_sphere = None
        close_point_distance = numpy.inf

        # Iterate through all spheres and see if we hit any
        spheres = self.spheres
        for sphere in spheres:
            # Get Model View Matrix 
            mm = numpy.array([
                [float(sphere.scale[0]), 0, 0, sphere.loc.x],
                [0, float(sphere.scale[1]), 0, sphere.loc.y], 
                [0, 0, float(sphere.scale[2]), sphere.loc.z],  
                [0, 0,                      0,            1]])
            # Get inverte and transpose
            mm_invt = numpy.linalg.inv(mm)
            mm_invt.transpose()
            
            # Multiply ray by Transoformation matrix
            c_val = numpy.matmul(mm_invt, [dir.x, dir.y, dir.z, 0])
            s_val = numpy.matmul(mm_invt, [start.x, start.y, start.z , 1])

            # Calculate Polynomial 
            a = pow(c_val[0], 2) + pow(c_val[1], 2) + pow(c_val[2], 2)
            b = numpy.dot(s_val, c_val)
            c = pow(s_val[0], 2) + pow(s_val[1], 2) + pow(s_val[2], 2) -1
            
            # Quadratic value
            intersections = (b**2) - (a*c)

            t1 = 0 # Distance value
            
            # Check our quadratic value
            if intersections < 0:
                # We miss
                t1 = numpy.inf
            elif intersections == 0.0:
                # One hit (We just brush against the sphere)
                t1 = -(b)/(a)
            else:
                # We hit the sphere
                t1 = -(b) / (a) + (numpy.sqrt(intersections)) / (a) 
                t2 = -(b) / (a) - (numpy.sqrt(intersections)) / (a)
                # Get lowest t
                if t2 < t1 and t2 > 0.000001:
                    t1 = t2

            # If we start at eye, check that our z values is beyond the image plane
            if start == self.eye:
                close_point = start + dir*t1
                # If the point doesn't go to infinity, and our z values is beyond the image plane Update values
                if t1 < close_point_distance and close_point.z < -1.000001:
                    close_point_distance = t1
                    close_sphere = sphere
            else: # If we don't start at eye, don't check for image plane, only for point going to infinity
                # If point goes to infinity and that the point isn't 0
                if t1 < close_point_distance and t1 > 0.000001:

                    close_point_distance = t1
                    close_sphere = sphere

        return  close_point_distance, close_sphere

    def _calculate_shadow_ray(self, light, sphere, point):
        # Colors to use later
        diffuse = Color.Color([0.0, 0.0, 0.0])
        specular = Color.Color([0.0, 0.0, 0.0])

        # Direction from point to light      
        light_vec = light.loc - point

        # Find closest Sphere   
        distance, close_sphere = self._closest_intersection(light_vec, point)

        # Check closest sphere
        if close_sphere is None:
            
            # Get Model View Matrix 
            mm = numpy.array([
                [float(sphere.scale[0]), 0, 0, sphere.loc.x],
                [0, float(sphere.scale[1]), 0, sphere.loc.y], 
                [0, 0, float(sphere.scale[2]), sphere.loc.z],  
                [0, 0,                      0,            1]])
            # Invert and transpose matrix
            mm_invt = numpy.linalg.inv(mm)
            mm_invt = mm_invt.transpose()

            # Get normal and normalize light vec
            normal = Point.Point(list(numpy.matmul(mm_invt, [point.x - sphere.loc.x, point.y - sphere.loc.y, point.z - sphere.loc.z, 0.0])[:3]))   
            normal = self._normalize(normal)
            light_vec = self._normalize(light_vec)

            # Find Diffuse
            d_var = max(numpy.dot(normal.values, light_vec.values), 0.0)
            kd = float(sphere.attributes[1])

            diffuse = Color.Color([
                kd * light.col.r * sphere.col.r * d_var,
                kd * light.col.g * sphere.col.g * d_var,
                kd * light.col.b * sphere.col.b * d_var
            ])
            
            # Get v and r values to calculate specular
            v = self._normalize(point * -1)
            r = self._normalize(light_vec - normal * 2 * numpy.dot(light_vec.values, normal.values))

            # Find Specular
            ks = float(sphere.attributes[2])
            spec_mod = ks * pow(max(numpy.dot(r.values, v.values), 0.0), float(sphere.attributes[4]))

            specular = Color.Color([
                spec_mod * light.col.r, 
                spec_mod * light.col.g, 
                spec_mod * light.col.b
            ])

        return diffuse, specular
    
    # Function that takes a ray, sphere and point as arguments. Returns the ray reflected at the point on the sphere
    def _calculate_reflection_ray(self, ray, sphere, point):

        # Get Model View Matrix 
        mm = numpy.array([
            [float(sphere.scale[0]), 0, 0, sphere.loc.x],
            [0, float(sphere.scale[1]), 0, sphere.loc.y], 
            [0, 0, float(sphere.scale[2]), sphere.loc.z],  
            [0, 0,                      0,            1]])
        # Invert and transpose matrix
        mm_invt = numpy.linalg.inv(mm)
        mm_invt = mm_invt.transpose()
        
        # Get normal
        normal = Point.Point(list(numpy.matmul(mm_invt,  [point.x - sphere.loc.x, point.y - sphere.loc.y, point.z - sphere.loc.z, 0.0]))[:3])
        normal = self._normalize(normal)

        # Get C
        c = self._normalize(ray.ray)

        # Get V
        v = normal * numpy.dot(normal.values, c.values) * -2 + c
        
        # Update ray values 
        ray.eye = point
        ray.ray = v 
        return ray
    
    # Function that normalizes a 3D vector
    def _normalize(self, point):

        len = numpy.linalg.norm(point.values)
        return Point.Point([point.x/len, point.y/len, point.z/len])
