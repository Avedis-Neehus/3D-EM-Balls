epsilon *= 10**6
mu*= 10**-6
c = 299.6
jit_EM_field.recompile()
new_charges(values = ['q = 8; V = [c/1.4,0,0]; X = [-25, 0, 0]', 'q = 8; V = [c/1.4,0,0]; X = [-25, 0, 25]' ])
scene.camera.follow(ballys[0].manifest) 