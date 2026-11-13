"""Fine-triangle metric distortion from 3D intrinsic coordinates to UV, with exclusions explicit."""
import numpy as np

def measure(vertices,faces,uv):
    tri3=np.asarray(vertices,dtype=float)[faces]; tri2=np.asarray(uv,dtype=float)[faces]
    e1=tri3[:,1]-tri3[:,0];e2=tri3[:,2]-tri3[:,0]
    l=np.linalg.norm(e1,axis=1);cross=np.linalg.norm(np.cross(e1,e2),axis=1)
    area3=cross/2
    intrinsic=np.zeros((len(faces),2,2));intrinsic[:,0,0]=l
    intrinsic[:,0,1]=np.einsum('ij,ij->i',e1,e2)/l;intrinsic[:,1,1]=cross/l
    edges=np.stack([tri2[:,1]-tri2[:,0],tri2[:,2]-tri2[:,0]],axis=-1)
    # Direct 2x2 determinant preserves exact repeated vertices; LU det can leave residue.
    signed=(edges[:,0,0]*edges[:,1,1]-edges[:,0,1]*edges[:,1,0])/2
    finite=np.isfinite(edges).all((1,2));nonzero=finite&(signed!=0)&(area3>0)
    singular=np.full((len(faces),2),np.nan)
    singular[nonzero]=np.linalg.svd(edges[nonzero]@np.linalg.inv(intrinsic[nonzero]),compute_uv=False)
    positive=nonzero&(signed>0)
    def summarize(mask):
        s=singular[mask];w=area3[mask];w=w/w.sum()
        symmetric=(s*s+1/(s*s)).sum(1)/4
        inverse_l2=np.sqrt((1/(s*s)).sum(1)/2)
        ratio=s.prod(1)
        return {'faces':int(mask.sum()),'area3_fraction':float(area3[mask].sum()/area3.sum()),
                'area_weighted_normalized_symmetric_dirichlet':float(w@symmetric),
                'area_weighted_inverse_L2_rms':float(np.sqrt(w@(inverse_l2*inverse_l2))),
                'max_symmetric_singular_stretch':float(np.maximum(s,1/s).max()),
                'uv_area_over_3d_area':float((ratio*area3[mask]).sum()/area3[mask].sum()),
                'area_ratio_percentiles_1_50_99':np.percentile(ratio,[1,50,99]).tolist(),
                'normalized_symmetric_dirichlet_percentiles_50_95_99':np.percentile(symmetric,[50,95,99]).tolist()}
    result={'input_faces':len(faces),'area3_total':float(area3.sum()),'invalid_uv_faces':int((~finite).sum()),
            'zero_uv_area_faces':int((finite&(signed==0)).sum()),'negative_uv_area_faces':int((finite&(signed<0)).sum()),
            'undefined_or_nonpositive_uv_area_fraction':float(area3[~positive].sum()/area3.sum()),
            'positive_faces_only':summarize(positive),'notes':'J maps the intrinsic 3D triangle to UV. Normalized symmetric Dirichlet is sum(sigma^2+sigma^-2)/4 with isometry=1. Invalid, collapsed, and inverted faces are reported separately, not assigned zero distortion.'}
    return result,{'area3':area3,'signed_uv_area':signed,'singular_values':singular,'positive_faces':positive}
