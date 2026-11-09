"""Bounded inspection of intended model-delivered ZIP artifacts for public copies."""
import hashlib,io,re,stat,zipfile
from pathlib import PurePosixPath
from release_privacy import sanitize
SECRET=re.compile(rb'sk-(?:proj-)?[A-Za-z0-9_-]{32,}')
PRIVATE_DIRS={'.git','.codex','.venv','venv','node_modules'}
PRIVATE_NAMES={'auth.json','credentials.json','id_rsa','id_ed25519'}
def inspect_zip(data,depth=0):
    if depth>2:raise ValueError('nested ZIP recursion limit exceeded')
    entries=[];changes=[]
    with zipfile.ZipFile(io.BytesIO(data))as archive:
        infos=archive.infolist()
        if len(infos)>5000 or sum(x.file_size for x in infos)>100_000_000:raise ValueError('nested ZIP size/member budget exceeded')
        for info in infos:
            name=info.filename.replace('\\','/');path=PurePosixPath(name)
            if name.startswith('/')or re.match(r'^[A-Za-z]:',name)or'..'in path.parts or stat.S_ISLNK(info.external_attr>>16):
                changes.append({'member':name,'action':'omitted','reason':'unsafe_path_or_symlink'});continue
            if info.file_size>20_000_000:raise ValueError('nested member exceeds20MB limit')
            if any(p.lower()in PRIVATE_DIRS for p in path.parts)or path.name.lower()in PRIVATE_NAMES or(path.name.lower().startswith('.env')and path.name.lower()!='.env.example'):
                changes.append({'member':name,'action':'omitted','reason':'local_environment_or_credential_file'});continue
            original=archive.read(info)
            if SECRET.search(original):
                changes.append({'member':name,'action':'omitted','reason':'potential_secret_string','original_sha256':hashlib.sha256(original).hexdigest()});continue
            if name.lower().endswith('.zip')and not info.is_dir():
                clean,nested=inspect_zip(original,depth+1);events=[{'nested_archive':nested}]if nested['changes']else[]
            else:clean,events=sanitize(name,original)
            if events:
                changes.append({'member':name,'action':'sanitized','original_sha256':hashlib.sha256(original).hexdigest(),
                                'sanitized_sha256':hashlib.sha256(clean).hexdigest(),'events':events})
            entries.append((info,clean))
    if changes:
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as archive:
            for info,contents in entries:archive.writestr(info,contents)
        clean=stream.getvalue()
    else:clean=data
    return clean,{'scan':'bounded_zip_privacy_secret_and_path_scan','depth':depth,'members':len(infos),
                  'uncompressed_bytes':sum(x.file_size for x in infos),'changes':changes,
                  'original_sha256':hashlib.sha256(data).hexdigest(),'public_sha256':hashlib.sha256(clean).hexdigest(),
                  'original_artifact_unchanged':not changes}
